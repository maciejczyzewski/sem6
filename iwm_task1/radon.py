import os
import time
import numpy as np
from PIL import Image
from numba import jit
from copy import copy
from pprint import pprint
import matplotlib.pyplot
from skimage import exposure
from scipy.fftpack import fft, ifft, fftfreq
import sys, IPython.core.ultratb
from tqdm import tqdm

oo = +4294967295  # tak wyglada nieskonczonosc
sys.excepthook = IPython.core.ultratb.ColorTB()

import pydicom

# ref: https://dicom.innolitics.com/ciods/cr-image/general-image/00080023

# [MUSIC]
# 46 minutes // looped https://www.youtube.com/watch?v=e8LLu4SPnSo
# 10 minutes // looped https://www.youtube.com/watch?v=tjRe2l64_v8
# mhmhm, dzis pojde pozno spac

CONFIG = {
    "path": "data/Shepp_logan.jpg",
    "shape": (320, 320),
    "alpha": 180 / (360),
    "rays": 360,
    "l": 270 / np.pi,
    "filtered": True,
}

"""
CONFIG = {
    "path": "data/Shepp_logan.jpg",
    "shape": (600, 600),
    "alpha": 0.5,
    "rays": 1000,
    "l": 600 / np.pi,
    "filtered": True,
}
"""

"""
CONFIG = {
    "path": "data/Shepp_logan.jpg",
    "shape": (320, 320),
    "alpha": 180 / (2 * 90),
    "rays": 2 * 90,
    "l": 4 * 45 / np.pi,
    "filtered": True,
}
"""

"""
CONFIG = {
    "path": "data/SADDLE_PE.JPG",
    # "path": "data/Shepp_logan.jpg",
    # "path": "data/CT_ScoutView.jpg",
    "shape": (600, 600),
    "alpha": 0.5,
    "rays": 2000,
    "l": 100,  # XXX: l -> powinno byc male
    "filtered": True,
}
"""

################################################################################


def fn_save(filename, img, cmap="viridis"):
    matplotlib.pyplot.imsave(filename, img, cmap=cmap)


def fn_load(filename):
    img = Image.open(filename).convert("L")
    img = img.resize(CONFIG["shape"], Image.ANTIALIAS)
    img = fn_clip(np.asarray(img), val=255)
    return np.asarray(img, dtype="int32")


def _fast_fn_noise_reduction(img):
    """tylko dla testu"""
    from skimage.restoration import denoise_nl_means, estimate_sigma

    sigma_est = np.mean(estimate_sigma(img, multichannel=True))

    sigma = 0.08
    patch_kw = dict(
        patch_size=5,  # 5x5 patches
        patch_distance=6,  # 13x13 search area
        multichannel=True,
    )

    return denoise_nl_means(img, h=0.8 * sigma_est, fast_mode=True, **patch_kw)


def fn_clip(img, val=1.0, agressive=False):
    img = img.astype(float) * 255
    img[img < 0] = 0
    img *= 1 / img.max()

    if agressive:  # blackhole solutions
        img = _fast_fn_noise_reduction(img)
        if CONFIG["rays"] >= 1000:
            p2, p98 = np.percentile(img, (0.5, 99.5))
        else:
            img = exposure.adjust_log(img, 1)
            p2, p98 = np.percentile(img, (2, 98))
        img = exposure.rescale_intensity(img, in_range=(p2, p98))

    return img * 255


def fn_calc_rmse(A, B):
    """Calculates the root mean square error (RSME) between two images"""
    A, B = fn_clip(A), fn_clip(B)
    errors = np.asarray(A - B) / 255
    return np.sqrt(np.mean(np.square(errors)))


def fn_calc_mse(A, B):
    # XXX: faster than RMSE (debug only)
    A, B = fn_clip(A), fn_clip(B)
    return ((A - B) ** 2).mean(axis=None)


@jit(nopython=True, nogil=True, fastmath=True)
def fn_line(x0, y0, x1, y1, X, Y):
    """https://gist.github.com/hallazzang/df3fde293e875892be02"""
    dx = int(x1 - x0)
    dy = int(y1 - y0)
    if dy < 0:
        dy = -dy
        stepy = -1
    else:
        stepy = 1
    if dx < 0:
        dx = -dx
        stepx = -1
    else:
        stepx = 1
    dx <<= 2
    dy <<= 2
    pixels = [(x0, y0) for _ in range(0)]
    if dx > dy:
        fraction = dy - (dx >> 1)
        while x0 != x1:
            if fraction >= 0:
                y0 += stepy
                fraction -= dx
            x0 += stepx
            fraction += dy
            if x0 < 0 or y0 < 0 or x0 >= X or y0 >= Y:
                continue
            pixels.append((x0, y0))
    else:
        fraction = dx - (dy >> 1)
        while y0 != y1:
            if fraction >= 0:
                x0 += stepx
                fraction -= dy
            y0 += stepy
            fraction += dx
            if x0 < 0 or y0 < 0 or x0 >= X or y0 >= Y:
                continue
            pixels.append((x0, y0))
    return pixels


def fn_autoparam(CONFIG, shape):
    alpha = CONFIG["alpha"]
    # [old] optimal_l = 0.5 * max(*shape)
    optimal_rays = max(2, int((alpha) * min(*shape) / 180))
    optimal_rays += optimal_rays % 2 == 0  # XXX: promien srodkowy
    if CONFIG["rays"] is None:
        CONFIG["rays"] = optimal_rays
    if CONFIG["l"] is None or CONFIG["l"] == 0:
        CONFIG["l"] = CONFIG["rays"] / np.pi
    return CONFIG


def fn_tomograph(img, alpha, rays, l, cone=False):
    # FIXME: co z debugowaniem???
    sinogram, lines = _fast_fn_tomograph(img, alpha, rays, l, cone=cone)
    return np.rot90(sinogram), lines


@jit(nopython=True, nogil=True, fastmath=True)
def _fast_fn_tomograph(img, alpha, rays, l, cone=False):
    d2r = lambda x: float(x) * float(np.pi / 180)

    i = 0
    Sw, Sh = img.shape
    size = max(Sw, Sh)

    diff = int(abs(Sw - Sh))
    diff_x0, diff_y0 = 0, 0
    if Sw < Sh:
        diff_x0 = -diff
    else:
        diff_y0 = -diff

    sinogram = []
    lines = []
    while i < 180:
        # print("@1", i, "/", 180)

        linogram = []
        ray_lines = []

        for ray in range(0, rays):
            shift = -(l / 2) + ray * l / (rays - 1)

            if not cone:
                x0 = size * np.cos(d2r(i - shift))
                y0 = size * np.sin(d2r(i - shift))
            else:
                x0 = size * np.cos(d2r(i))
                y0 = size * np.sin(d2r(i))

            x1 = (size) * np.cos(d2r(i + 180 + shift))
            y1 = (size) * np.sin(d2r(i + 180 + shift))

            x0 = diff_x0 + int(x0) + size // 2
            x1 = int(x1) + size // 2
            y0 = diff_y0 + int(y0) + size // 2
            y1 = int(y1) + size // 2

            line = fn_line(x0, y0, x1, y1, X=Sw, Y=Sh)

            S = 0
            for p in line:
                S += img[int(p[1]), int(p[0])]

            linogram.append(S)
            ray_lines.append([x0, y0, x1, y1])

        sinogram.append(linogram)
        lines.append(ray_lines)

        i += alpha

    sinogram = np.array(sinogram)
    lines = np.array(lines)

    return sinogram, lines


def fn_fbp(shape, sinogram, lines, filtered=True, debug=True, n_slices=6):
    img = np.zeros(shape)

    if filtered:
        # XXX: znaleziony filtr (https://www.youtube.com/watch?v=pZ7JlXagT0w)
        f = fftfreq(sinogram.shape[0]).reshape(-1, 1)  # digital frequency
        omega = 2 * np.pi * f  # angular frequency
        fourier_filter = 2 * np.abs(f)  # ramp filter

        projection = fft(sinogram, axis=0) * fourier_filter
        sinogram = np.real(ifft(projection, axis=0))

    if not debug:
        return np.rot90(
            _fast_fn_fbp(
                img, shape, sinogram, lines, left=0, right=sinogram.shape[1]
            ),
            k=2,
        )

    imgs = []

    for i in range(n_slices):
        gap = sinogram.shape[1] // n_slices
        left, right = i * gap, (i + 1) * gap
        # print(f"[slice={i}] left={left} right={right}")
        img = _fast_fn_fbp(img, shape, sinogram, lines, left=left, right=right)
        imgs.append(np.rot90(copy(img), k=2))

    return imgs


@jit(nopython=True, nogil=True, fastmath=True)
def _fast_fn_fbp(img, shape, sinogram, lines, left=0, right=+oo):
    for i in range(left, right):
        # print("@2", i, "/", sinogram.shape[1])
        for ray in range(sinogram.shape[0]):
            value = sinogram[ray][i]
            x0, y0, x1, y1 = lines[i][ray]
            for p in fn_line(x0, y0, x1, y1, X=shape[0], Y=shape[1]):
                img[int(p[1]), int(p[0])] += value
    return img


################################################################################


def fn_load_dicom(filename="data/test.dcm"):
    ds = pydicom.dcmread(filename)

    if "PatientName" in ds:
        print(f"\033[91m=== PatientName: {ds.PatientName}\033[m")
    if "ImageComments" in ds:
        print(f"\033[91m=== ImageComments: {ds.ImageComments}\033[m")
    if "StudyDate" in ds:
        print(f"\033[91m=== StudyDate: {ds.StudyDate}\033[m")

    arr = ds.pixel_array
    img = Image.fromarray(np.uint8(arr * 255))
    img = img.resize(CONFIG["shape"], Image.ANTIALIAS)
    img = fn_clip(np.asarray(img), val=255)
    return np.asarray(img, dtype="int32")


def fn_save_dicom(filename="data/test.dcm", data={}):
    if isinstance(filename, str):
        ds = pydicom.dcmread(filename)
    else:
        ds = filename  # object, hotfix

    if "PatientName" in data:
        ds.PatientName = data["PatientName"]
    if "ImageComments" in data:
        ds.ImageComments = data["ImageComments"]
    if "StudyDate" in data:
        ds.StudyDate = data["StudyDate"]

    ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRBigEndian
    ds.is_little_endian = False
    ds.is_implicit_VR = False
    ds.save_as(filename)


################################################################################


def fn_rmse(img, CONFIG):
    CONFIG = fn_autoparam(CONFIG, img.shape)
    pprint(CONFIG)

    print("[1 step] img -> sinogram (~3 sec)")
    sinogram, lines = fn_tomograph(
        img, alpha=CONFIG["alpha"], rays=CONFIG["rays"], l=CONFIG["l"]
    )

    print("[2 step] sinogram -> img (~3 sec)")
    ctimg = fn_fbp(
        img.shape, sinogram, lines, filtered=CONFIG["filtered"], n_slices=6
    )

    print("[3 step] processing")
    ctimg_clip = fn_clip(ctimg[-1], agressive=CONFIG["filtered"])

    rmse = fn_calc_rmse(ctimg_clip, img)
    print(f"RMSE={rmse}")
    return rmse


################################################################################

if __name__ == "__main__ (all)":
    img = fn_load(CONFIG["path"])
    CONFIG_DEFAULT = copy(CONFIG)

    rp, rn = 200, 8
    ap, an = 90, 8
    lp, ln = 45, 20

    """
    rp, rn = 90, 8
    ap, an = 90, 8
    lp, ln = 45, 6
    """

    rmse = 0

    Y_R, X_R = [], []
    CONFIG = copy(CONFIG_DEFAULT)
    for P in tqdm(range(1, rn + 1)):
        print(f"\033[92mP={P}\033[m")
        CONFIG["rays"] = P * rp
        rmse = fn_rmse(img, CONFIG)
        X_R.append(P * rp)
        Y_R.append(rmse)

    Y_A, X_A = [], []
    CONFIG = copy(CONFIG_DEFAULT)
    for P in tqdm(range(1, an + 1)):
        print(f"\033[92mP={P}\033[m")
        CONFIG["alpha"] = 180 / (P * ap)
        rmse = fn_rmse(img, CONFIG)
        X_A.append(P * ap)
        Y_A.append(rmse)

    Y_L, X_L = [], []
    CONFIG = copy(CONFIG_DEFAULT)
    for P in tqdm(range(1, ln + 1)):
        print(f"\033[92mP={P}\033[m")
        CONFIG["l"] = (P * lp) / np.pi
        rmse = fn_rmse(img, CONFIG)
        X_L.append(P * lp)
        Y_L.append(rmse)

    print("R")
    pprint(Y_R)

    print("A")
    pprint(Y_A)

    print("L")
    pprint(Y_L)

################################################################################

if __name__ == "__main__":
    img = fn_load(CONFIG["path"])
    CONFIG = fn_autoparam(CONFIG, img.shape)
    pprint(CONFIG)

    print("[1 step] img -> sinogram (~3 sec)")
    sinogram, lines = fn_tomograph(
        img, alpha=CONFIG["alpha"], rays=CONFIG["rays"], l=CONFIG["l"]
    )

    fn_save("1_sinogram.png", sinogram)

    print("[2 step] sinogram -> img (~3 sec)")
    ctimg = fn_fbp(
        img.shape, sinogram, lines, filtered=CONFIG["filtered"], n_slices=6
    )

    fn_save("2_ctimg.png", ctimg[-1])

    print("[3 step] processing")
    ctimg_clip = fn_clip(ctimg[-1], agressive=CONFIG["filtered"])

    fn_save("3_ctimg_clip.png", ctimg_clip)
    fn_save("3_ctimg_orginal.png", img)

    print(f"RMSE={fn_calc_rmse(ctimg_clip, img)}")
