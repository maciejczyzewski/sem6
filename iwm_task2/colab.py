import sys, IPython.core.ultratb

sys.excepthook = IPython.core.ultratb.ColorTB()

print("[CHASEDB1]")

# packages
"""
%reload_ext autoreload
%autoreload 0
%matplotlib inline
!pip install --upgrade -r requirements.txt
!pip install --no-cache-dir -I pillow
"""

# colab trick
"""
function ClickConnect(){
  console.log("Working"); 
  document
    .querySelector("#top-toolbar > colab-connect-button")
    .shadowRoot
    .querySelector("#connect")
    .click()
}
setInterval(ClickConnect,60000)
"""

# clean memory
"""
import torch
torch.cuda.empty_cache()
"""

# tym razem robione przy:
# - https://soundcloud.com/dafresh/da-fresh-fuckin-track-da-fresh
# - https://soundcloud.com/wiewouwat/henrik-schwarz-not-also-you-running-back
# - https://soundcloud.com/joppewouts2/open-eye-signal-george-fitzgerald-remix
# - https://soundcloud.com/last-night-on-earth/hobo-levitate
# - https://www.youtube.com/watch?v=USXIRaeshsU&t=0s

# dobry resource:
# https://github.com/usuyama/pytorch-unet

import os
import time
import copy
import math
import random
import argparse
import numpy as np
from glob import glob
from tqdm import tqdm
from scipy import ndimage
import matplotlib.pyplot as plt
from skimage import io, exposure
from skimage.filters import unsharp_mask
from sklearn.model_selection import train_test_split
from collections import defaultdict
from functools import reduce
from PIL import Image

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
from torch.optim import Optimizer, Adam, lr_scheduler
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms.functional as TF
from torchvision import transforms, datasets, models
from torchsummary import summary

"""
SHAPE = (32, 32)
BATCH_SIZE = 128
NUM_EPOCHS = 15
N_FOLDS = 3

N_TRAIN = 6000
N_TEST = 6000
N_SPREAD = 6000
"""

SHAPE = (64, 64)
BATCH_SIZE = 32
NUM_EPOCHS = 5
N_FOLDS = 1

N_TRAIN = 256
N_TEST = 256
N_SPREAD = 256

################################################################################

torch.backends.cudnn.deterministic = True
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

parser = argparse.ArgumentParser(description="PyTorch CHASEDB1 Training")
parser.add_argument("--train", "-t", action="store_true")
parser.add_argument("--test", "-p", action="store_true")
args = parser.parse_args()

################################################################################


class RetinalDataset:
    path_original = ""
    path_preprocess = ""

    X, Y = [], []
    ids, imgs = [], []

    def __init__(self, root_dir="CHASEDB1"):
        self.path_original = f"{root_dir}/original"
        self.path_preprocess = f"{root_dir}/preprocess"

        self.ids = [
            f.split("Image_")[1].replace(".jpg", "")
            for f in glob(self.path_original + "/Image_*")
            if "HO" not in f
        ]

    def load(self):
        X, Y = [], []
        for idx in self.ids:
            print(idx, self._path_p(idx))
            X.append(io.imread(self._path_p(idx, suffix="_x")))
            Y.append(io.imread(self._path_p(idx, suffix="_y")))
        self.X, self.Y = np.array(X), np.array(Y)
        return self.X, self.Y

    def preprocess(self, force=False):
        if not os.path.exists(self.path_preprocess) or force:
            os.makedirs(self.path_preprocess, exist_ok=True)
            self._preprocess_x()
            self._preprocess_y()

    def _path_o(self, idx, suffix="", ext=".jpg"):
        return self.path_original + "/Image_" + idx + suffix + ext

    def _path_p(self, idx, suffix="", ext=".jpg"):
        return self.path_preprocess + "/" + idx + suffix + ext

    def _preprocess_x(self):
        print("\033[92m[MASK]\033[0m")

        for idx in tqdm(self.ids):
            io.imsave(
                self._path_p(idx, suffix="_y"),
                io.imread(self._path_o(idx, suffix="_1stHO", ext=".png"))
                + io.imread(self._path_o(idx, suffix="_2ndHO", ext=".png")),
            )
            self.imgs.append(io.imread(self._path_o(idx), as_gray=True))

    def _preprocess_y(self):
        print("\033[92m[IMAGE]\033[0m")
        self.imgs = RetinalDataset.normalize(np.array(self.imgs))

        for i in tqdm(range(len(self.ids))):
            io.imsave(
                self._path_p(self.ids[i], suffix="_x"),
                RetinalDataset.block(self.imgs[i].astype(int)),
            )

    @staticmethod
    def block(img):
        # FIXME: grid searchowac ten fragment?
        """ agressive
        from skimage.morphology import disk
        from skimage.filters import rank
        selem = disk(30)
        img = rank.equalize(img, selem=selem)
        img = exposure.equalize_adapthist(img)
        img = exposure.adjust_gamma(img)
        img = unsharp_mask(img, radius=5, amount=2)
        img = ndimage.uniform_filter(img, size=4)"""
        img = exposure.equalize_adapthist(img)
        img = exposure.adjust_gamma(img)
        img = unsharp_mask(img, radius=3, amount=2)
        img = ndimage.uniform_filter(img, size=2)
        return (img * 255).astype(np.uint8)

    @staticmethod
    def normalize(imgs):
        _imgs = np.empty(imgs.shape)
        _imgs = (imgs - np.mean(imgs)) / np.std(imgs)
        for i in range(imgs.shape[0]):
            _imgs[i] = (
                (_imgs[i] - np.min(_imgs[i]))
                / (np.max(_imgs[i]) - np.min(_imgs[i]))
            ) * 255
        return _imgs


_cache_dataset = None


def _setup_dataset(root_dir="CHASEDB1"):
    global _cache_dataset
    if _cache_dataset is not None:
        return _cache_dataset
    if not os.path.exists(root_dir):
        os.system(
            "wget https://staffnet.kingston.ac.uk/~ku15565/CHASE_DB1/assets/CHASEDB1.zip"
        )
        os.system("mkdir CHASEDB1")
        os.system("unzip CHASEDB1.zip -d CHASEDB1/original")

    dataset = RetinalDataset(root_dir)
    dataset.preprocess(force=False)
    dataset.load()
    _cache_dataset = dataset
    return _cache_dataset


def get_dataset():
    dataset = _setup_dataset()

    X_train, X_test, y_train, y_test = train_test_split(
        dataset.X, dataset.Y, test_size=0.15, random_state=42
    )

    return X_train, X_test, y_train, y_test


################################################################################


class DetectorDataset(Dataset):
    def __init__(self, count, _X, _Y, shape=(32, 32), transform=None):
        self.X, self.Y = _X, _Y
        self.input_images, self.target_masks, self.positions = self.generate(
            size=count, shape=shape
        )
        self.transform = transform

    def generate(self, size=512, shape=(32, 32)):
        # FIXME: tryb losowanie tylko wogol pewnych punktow
        X_batch, y_batch, P_batch = [], [], []
        for _ in tqdm(range(size)):
            while 1:
                idx = random.randint(0, len(self.X) - 1)
                i = random.randint(0, self.X[0].shape[0] - shape[0])
                j = random.randint(0, self.X[0].shape[1] - shape[1])
                a = self.X[idx][i : (i + shape[0]), j : (j + shape[1])]
                b = self.Y[idx][i : (i + shape[0]), j : (j + shape[1])]
                if a.mean() < 20:  # FIXME
                    continue
                X_batch.append(Image.fromarray(np.uint8(a)))
                y_batch.append(Image.fromarray(np.uint8(b)))
                P_batch.append([i, j])
                break
        return X_batch, y_batch, P_batch

    def merge(self, pred, shape=(32, 32)):
        # FIXME: aktualnie potrafi tylko dla jednego
        # a nie wielu rownoczesnie (trzeba zapisywac X:idx)
        assert len(self.X) == 1
        mask = np.zeros(self.X[0].shape)

        for idx in tqdm(range(len(pred))):
            img = pred[idx].reshape(shape)
            i, j = self.positions[idx]
            mask_avg = mask[i : (i + shape[0]), j : (j + shape[1])]
            mask[i : (i + shape[0]), j : (j + shape[1])] = (
                mask_avg + img * 255
            ) / 2

        return mask

    def __len__(self):
        return len(self.input_images)

    def __getitem__(self, idx):
        image = self.input_images[idx]
        mask = self.target_masks[idx]
        if self.transform:
            seed = np.random.randint(2147483647)
            random.seed(seed)
            torch.manual_seed(seed)
            torch.cuda.manual_seed(seed)
            image = self.transform(image)

            random.seed(seed)
            torch.manual_seed(seed)
            torch.cuda.manual_seed(seed)
            mask = self.transform(mask)
        return [image, mask]


################################################################################

# class RandomRotateTransform:
#     def __init__(self, angles: list):
#         self.angles = angles

#     def __call__(self, x):
#         angle = random.choice(self.angles)
#         return TF.rotate(x, angle)


trans = transforms.Compose(
    [
        # RandomRotateTransform(angles=[0, 90, 180, 270]),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.ToTensor(),
    ]
)

from sklearn.model_selection import KFold

kfolds_split = {}


def get_dataloaders(k=1):
    global kfolds_split
    X_train, X_test, y_train, y_test = get_dataset()

    if N_FOLDS == 1:
        return {
            "train": DataLoader(
                DetectorDataset(
                    N_TRAIN, X_train, y_train, shape=SHAPE, transform=trans
                ),
                batch_size=BATCH_SIZE,
                shuffle=True,
                num_workers=0,
            ),
            "val": DataLoader(
                DetectorDataset(
                    N_TEST, X_test, y_test, shape=SHAPE, transform=trans
                ),
                batch_size=BATCH_SIZE,
                shuffle=True,
                num_workers=0,
            ),
            "test": DataLoader(
                DetectorDataset(
                    N_TEST, X_test, y_test, shape=SHAPE, transform=trans
                ),
                batch_size=BATCH_SIZE,
                shuffle=True,
                num_workers=0,
            ),
        }

    if not kfolds_split:
        for i, (train_index, val_index) in enumerate(
            KFold(n_splits=N_FOLDS).split(X_train)
        ):
            kfolds_split[i] = {"train": train_index, "val": val_index}

    return {
        "train": DataLoader(
            DetectorDataset(
                int(((N_FOLDS - 1) / N_FOLDS) * N_TRAIN),
                X_train[kfolds_split[k]["train"]],
                y_train[kfolds_split[k]["train"]],
                shape=SHAPE,
                transform=trans,
            ),
            batch_size=BATCH_SIZE,
            shuffle=True,
            num_workers=0,
        ),
        "val": DataLoader(
            DetectorDataset(
                int(((1) / N_FOLDS) * N_TRAIN),
                X_train[kfolds_split[k]["val"]],
                y_train[kfolds_split[k]["val"]],
                shape=SHAPE,
                transform=trans,
            ),
            batch_size=BATCH_SIZE,
            shuffle=True,
            num_workers=0,
        ),
        "test": DataLoader(
            DetectorDataset(
                N_TEST, X_test, y_test, shape=SHAPE, transform=trans
            ),
            batch_size=BATCH_SIZE,
            shuffle=True,
            num_workers=0,
        ),
    }


################################################################################


def convrelu(in_channels, out_channels, kernel, padding):
    return nn.Sequential(
        nn.Conv2d(in_channels, out_channels, kernel, padding=padding),
        nn.ReLU(inplace=True),
    )


class UUUnet(nn.Module):
    def __init__(self, n_class):
        super().__init__()

        self.base_model = models.resnet18(pretrained=True)
        self.base_layers = list(self.base_model.children())

        self.layer0 = nn.Sequential(
            nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
        )
        self.layer0_1x1 = convrelu(64, 64, 1, 0)

        self.layer1 = nn.Sequential(*self.base_layers[3:5])

        self.upsample = nn.Upsample(
            scale_factor=2, mode="bilinear", align_corners=False
        )

        self.conv_bn = nn.BatchNorm2d(64)

        self.conv_original_size0 = convrelu(1, 64, 3, 1)
        self.conv_original_size1 = convrelu(192, 64, 3, 1)

        self.conv_last = nn.Conv2d(64, 1, 1, padding=0, bias=False)

    def forward(self, input):
        x_original = self.conv_original_size0(input)

        layer0 = self.layer0(input)
        layer1 = self.layer1(layer0)

        x = self.upsample(layer1)
        layer0 = self.layer0_1x1(layer0)
        layer0 = self.conv_bn(layer0)
        x = torch.cat([x, layer0], dim=1)

        x = self.upsample(x)
        x = torch.cat([x, x_original], dim=1)
        x = self.conv_original_size1(x)

        out = self.conv_last(x)

        return out


_cache_model = None


def get_model(root_dir="weights"):
    global _cache_model
    if _cache_model is not None:
        return _cache_model
    model = UUUnet(n_class=2)
    model = model.to(DEVICE)

    google_drive_weights = (
        "https://drive.google.com/uc?id=1RFlr4IwW0Om9o3ICogJOhBmkbxTE9kFN"
    )

    if not os.path.exists(root_dir):
        os.system(f"pip3 uninstall -y enum34 && pip3 install gdown")
        os.system(f"gdown {google_drive_weights}")
        os.system(f"unzip weights.zip")

    try:
        print("\033[94mLOAD WEIGHTS\033[0m")
        model.load_state_dict(
            torch.load(
                f"{root_dir}/retinal_detector_{SHAPE[0]}", map_location=DEVICE
            )
        )
    except:
        os.makedirs(root_dir, exist_ok=True)
        print("\033[94mERROR\033[0m")

    summary(model, input_size=(1, *SHAPE))
    _cache_model = model
    return model


################################################################################


class BatchBoost:
    """
    batchboost: regularization for stabilizing training
                with resistance to underfitting & overfitting
    Maciej A. Czyzewski
    https://arxiv.org/abs/2001.07627
    """

    def __init__(
        self,
        alpha=1.0,
        window_normal=0,
        window_boost=10,
        factor=1 / 3,
        use_cuda=False,
        debug=False,
    ):
        self.alpha = alpha
        self.window_normal = window_normal
        self.window_boost = window_boost
        self.factor = factor
        self.use_cuda = use_cuda
        self.debug = debug
        self.clear()

        if self.debug:
            print(
                f"[BatchBoost] alpha={alpha} ratio={factor} \
window_normal={window_normal} window_boost={window_boost}"
            )

    def clear(self):
        if self.debug:
            print(f"[BatchBoost] resetting")
        self.mixup_lambda = 1
        self.inputs = None
        self.y1 = self.y2 = None
        self.iter_normal = self.window_normal
        self.iter_boost = self.window_boost

    @staticmethod
    def mixup(x, y, index_left, index_right, mixup_lambda=1.0):
        """Returns mixed inputs, pairs of targets, and lambda
        https://arxiv.org/abs/1710.09412"""
        mixed_x = (
            mixup_lambda * x[index_left, :]
            + (1 - mixup_lambda) * x[index_right, :]
        )
        # mixed_y = (mixup_lambda * y[index_left, :] +
        #           (1 - mixup_lambda) * y[index_right, :])
        # return mixed_x, mixed_y, mixup_lambda
        y1, y2 = y[index_left], y[index_right]
        return mixed_x, y1, y2

    @staticmethod
    def fn_error(outputs, targets):
        logsoftmax = nn.LogSoftmax(dim=1)
        return torch.sum(-outputs * logsoftmax(targets), dim=1)

    @staticmethod
    def fn_linearize(x, num_classes=10):
        _x = torch.zeros(x.size(0), num_classes)
        _x[range(x.size(0)), x] = 1
        return _x

    @staticmethod
    def fn_unlinearize(x):
        _, _x = torch.max(x, 1)
        return _x

    def criterion(self, criterion, outputs):
        _y1 = BatchBoost.fn_unlinearize(self.y1)
        _y2 = BatchBoost.fn_unlinearize(self.y2)
        return self.mixup_lambda * criterion(outputs, _y1) + (
            1 - self.mixup_lambda
        ) * criterion(outputs, _y2)

    def correct(self, predicted):
        _y1 = BatchBoost.fn_unlinearize(self.y1)
        _y2 = BatchBoost.fn_unlinearize(self.y2)
        return (
            self.mixup_lambda * predicted.eq(_y1).cpu().sum().float()
            + (1 - self.mixup_lambda) * predicted.eq(_y2).cpu().sum().float()
        )

    def pairing(self, errvec):
        batch_size = errvec.size()[0]
        _, index = torch.sort(errvec, dim=0, descending=True)
        return (
            index[0 : int(batch_size * self.factor)],
            reversed(index[batch_size - int(batch_size * self.factor) :]),
        )

    def mixing(self, outputs):
        if self.iter_boost + self.iter_normal == 0:
            self.iter_normal = self.window_normal
            self.iter_boost = self.window_boost
        if self.iter_boost > 0:
            if self.debug:
                print("[BatchBoost]: half-batch + feed-batch")
            errvec = BatchBoost.fn_error(outputs, self.targets)
            index_left, index_right = self.pairing(errvec)

            if self.alpha > 0:
                self.mixup_lambda = np.random.beta(self.alpha, self.alpha)
            else:
                self.mixup_lambda = 1

            self.inputs, self.y1, self.y2 = BatchBoost.mixup(
                self.inputs,
                y=self.targets,
                index_left=index_right,
                index_right=index_left,
                mixup_lambda=self.mixup_lambda,
            )

            self.iter_boost -= 1
        elif self.iter_normal > 0:
            if self.debug:
                print("[BatchBoost] normal batch")
            batch_size = self.inputs.size(0)
            self.inputs = self.inputs[int(batch_size * self.factor) :]
            self.y1 = self.y1[int(batch_size * self.factor) :]
            self.y2 = self.y2[int(batch_size * self.factor) :]
            self.mixup_lambda = 1
            self.iter_normal -= 1

    def feed(self, new_inputs, _new_targets):
        new_targets = Variable(BatchBoost.fn_linearize(_new_targets))
        if self.use_cuda:
            new_targets = new_targets.cuda()
        # no mixing (first iteration)
        if self.inputs is None:
            self.inputs = Variable(new_inputs)
            self.y1 = new_targets
            self.y2 = new_targets
            return False
        # concat
        self.inputs = torch.cat([self.inputs, new_inputs], dim=0)
        self.y1 = torch.cat([self.y1, new_targets], dim=0)
        self.y2 = torch.cat([self.y2, new_targets], dim=0)
        # virtual targets
        self.targets = (
            self.mixup_lambda * self.y1 + (1 - self.mixup_lambda) * self.y2
        )
        return True


################################################################################


def dice_loss_1(a, b, smooth=1.0):
    intersection = (a * b).sum()
    return 1 - ((2.0 * intersection + smooth) / (a.sum() + b.sum() + smooth))


def dice_loss(input, target, smooth=1.0):
    iflat = input.view(-1)
    tflat = target.view(-1)
    return dice_loss_1(iflat, tflat)


def calc_loss(pred, target, bce_weight=0.2):
    target = target.type_as(pred)
    bce = F.binary_cross_entropy_with_logits(pred, target)

    pred = torch.sigmoid(pred)
    dice = dice_loss(pred, target)

    loss = bce * bce_weight + dice * (1 - bce_weight)

    # metrics["bce"] += bce.data.cpu().numpy() * target.size(0)
    # metrics["dice"] += dice.data.cpu().numpy() * target.size(0)
    # metrics["loss"] += loss.data.cpu().numpy() * target.size(0)

    return loss


def print_metrics(metrics, epoch_samples, phase):
    outputs = []
    for k in metrics.keys():
        outputs.append("{}: {:4f}".format(k, metrics[k] / epoch_samples))

    print("{}: {}".format(phase.rjust(10), ", ".join(outputs)))


def loop(
    model,
    optimizer,
    scheduler,
    dataloaders,
    num_epochs=25,
    batchboost=None,
    root_dir="weights",
    best_loss=1e10,
):
    best_model_wts = copy.deepcopy(model.state_dict())

    BB = batchboost

    for epoch in range(num_epochs):
        print("[Epoch {}/{}]".format(epoch, num_epochs - 1))
        since = time.time()

        for phase in ["train", "val", "test"]:
            if phase == "test" and epoch != num_epochs - 1:
                continue

            if phase == "train":
                for param_group in optimizer.param_groups:
                    print("LR", param_group["lr"])

                model.train()
            else:
                model.eval()

            # FIXME: metrics are wrong
            metrics = defaultdict(float)
            epoch_samples = 0

            for inputs, labels in dataloaders[phase]:
                print("+", end="", flush=True)
                inputs = inputs.to(DEVICE)
                labels = labels.to(DEVICE)

                if phase == "train":
                    if not BB.feed(inputs, labels):
                        continue

                optimizer.zero_grad()

                with torch.set_grad_enabled(phase == "train"):
                    if phase == "train":
                        outputs = model(BB.inputs)
                        loss = BB.criterion(calc_loss, outputs)

                        loss.backward()
                        optimizer.step()
                    else:
                        outputs = model(inputs)
                        loss = calc_loss(outputs, labels)

                    metrics["loss"] += loss.data.cpu().numpy() * outputs.size(0)

                if phase == "train":
                    BB.mixing(outputs)

                epoch_samples += inputs.size(0)
            print()

            if phase == "train":
                scheduler.step()

            print_metrics(metrics, epoch_samples, phase)
            epoch_loss = metrics["loss"] / epoch_samples

            if phase == "val" and epoch_loss < best_loss:
                print("\033[94msaving best model\033[0m")
                best_loss = epoch_loss
                best_model_wts = copy.deepcopy(model.state_dict())
                torch.save(
                    best_model_wts, f"{root_dir}/retinal_detector_{SHAPE[0]}"
                )

        time_elapsed = time.time() - since
        print("{:.0f}m {:.0f}s".format(time_elapsed // 60, time_elapsed % 60))
        print()

    print("best val loss: \033[92m{:4f}\033[0m".format(best_loss))

    model.load_state_dict(best_model_wts)
    return model, best_loss


def predict(X):
    model = get_model()
    model.eval()

    squares = DetectorDataset(
        N_SPREAD, [X], [X], shape=SHAPE, transform=transforms.ToTensor()
    )

    batches = DataLoader(
        squares, batch_size=BATCH_SIZE, shuffle=False, num_workers=0
    )

    pred = np.array([])
    for inputs, labels in tqdm(batches):
        inputs = inputs.to(DEVICE)
        labels = labels.to(DEVICE)

        _pred = model(inputs)
        _pred = torch.sigmoid(_pred)
        _pred = _pred.data.cpu().numpy()
        if pred.shape[0] == 0:
            pred = _pred
            continue
        pred = np.concatenate((pred, _pred), axis=0)

    return squares.merge(pred, shape=SHAPE)


################################################################################

"""Lamb optimizer.
https://github.com/cybertronai/pytorch-lamb"""


class Lamb(Optimizer):
    r"""Implements Lamb algorithm.
    It has been proposed in `Large Batch Optimization for Deep Learning:
                                            Training BERT in 76 minutes`_.
    Arguments:
        params (iterable): iterable of parameters to optimize or dicts defining
            parameter groups
        lr (float, optional): learning rate (default: 1e-3)
        betas (Tuple[float, float], optional): coefficients used for computing
            running averages of gradient and its square (default: (0.9, 0.999))
        eps (float, optional): term added to the denominator to improve
            numerical stability (default: 1e-8)
        weight_decay (float, optional): weight decay (L2 penalty) (default: 0)
        adam (bool, optional): always use trust ratio = 1, which turns this into
            Adam. Useful for comparison purposes.
    .. _Large Batch Optimization for Deep Learning: Training BERT in 76 minutes:
        https://arxiv.org/abs/1904.00962
    """

    def __init__(
        self,
        params,
        lr=1e-3,
        betas=(0.9, 0.999),
        eps=1e-6,
        weight_decay=0,
        adam=False,
    ):
        if not 0.0 <= lr:
            raise ValueError("Invalid learning rate: {}".format(lr))
        if not 0.0 <= eps:
            raise ValueError("Invalid epsilon value: {}".format(eps))
        if not 0.0 <= betas[0] < 1.0:
            raise ValueError(
                "Invalid beta parameter at index 0: {}".format(betas[0])
            )
        if not 0.0 <= betas[1] < 1.0:
            raise ValueError(
                "Invalid beta parameter at index 1: {}".format(betas[1])
            )
        defaults = dict(lr=lr, betas=betas, eps=eps, weight_decay=weight_decay)
        self.adam = adam
        super(Lamb, self).__init__(params, defaults)

    def step(self, closure=None):
        """Performs a single optimization step.
        Arguments:
            closure (callable, optional): A closure that reevaluates the model
                and returns the loss.
        """
        loss = None
        if closure is not None:
            loss = closure()

        for group in self.param_groups:
            for p in group["params"]:
                if p.grad is None:
                    continue
                grad = p.grad.data
                if grad.is_sparse:
                    raise RuntimeError(
                        "Lamb does not support sparse gradients, consider SparseAdam instad."
                    )

                state = self.state[p]

                # State initialization
                if len(state) == 0:
                    state["step"] = 0
                    # Exponential moving average of gradient values
                    state["exp_avg"] = torch.zeros_like(p.data)
                    # Exponential moving average of squared gradient values
                    state["exp_avg_sq"] = torch.zeros_like(p.data)

                exp_avg, exp_avg_sq = state["exp_avg"], state["exp_avg_sq"]
                beta1, beta2 = group["betas"]

                state["step"] += 1

                # Decay the first and second moment running average coefficient
                # m_t
                exp_avg.mul_(beta1).add_(1 - beta1, grad)
                # v_t
                exp_avg_sq.mul_(beta2).addcmul_(1 - beta2, grad, grad)

                # Paper v3 does not use debiasing.
                bias_correction1 = 1 - beta1 ** state["step"]
                bias_correction2 = 1 - beta2 ** state["step"]
                # Apply bias to lr to avoid broadcast.
                step_size = (
                    group["lr"] * math.sqrt(bias_correction2) / bias_correction1
                )

                weight_norm = p.data.pow(2).sum().sqrt().clamp(0, 10)

                adam_step = exp_avg / exp_avg_sq.sqrt().add(group["eps"])
                if group["weight_decay"] != 0:
                    adam_step.add_(group["weight_decay"], p.data)

                adam_norm = adam_step.pow(2).sum().sqrt()
                if weight_norm == 0 or adam_norm == 0:
                    trust_ratio = 1
                else:
                    trust_ratio = weight_norm / adam_norm
                state["weight_norm"] = weight_norm
                state["adam_norm"] = adam_norm
                state["trust_ratio"] = trust_ratio
                if self.adam:
                    trust_ratio = 1

                p.data.add_(-step_size * trust_ratio, adam_step)

        return loss


################################################################################


def train():
    model = get_model()

    # [FIXME] freeze backbone layers
    # for l in model.base_layers:
    #    for param in l.parameters():
    #        param.requires_grad = False

    optimizer_ft = Lamb(model.parameters(), lr=1e-1, betas=(0.9, 0.999))
    exp_lr_scheduler = lr_scheduler.StepLR(optimizer_ft, step_size=3, gamma=0.5)

    def fn_error(outputs, targets):
        errvec = []
        for i in range(outputs.shape[0]):
            errvec.append(dice_loss_1(outputs[i], targets[i]))
        return torch.FloatTensor(errvec)

    BatchBoost.fn_error = fn_error
    BatchBoost.fn_linearize = lambda x: x
    BatchBoost.fn_unlinearize = lambda x: x

    BB = BatchBoost(
        alpha=0.5,
        window_normal=5,
        window_boost=10,
        factor=1 / 3,
        use_cuda=torch.cuda.is_available(),
    )

    # FIXME: po co k-folding bez ensemble learning?
    #        zeby to mialo sens kazdy split to powinnien byc inny model

    best_loss = 1e10
    for k in range(N_FOLDS):
        print(f"=== \033[90m(k={k+1}/{N_FOLDS})\033[0m ===")
        model, best_loss = loop(  # FIXME: define name of model
            model,
            optimizer_ft,
            exp_lr_scheduler,
            get_dataloaders(k),
            batchboost=BB,
            num_epochs=NUM_EPOCHS,
            best_loss=best_loss,
        )  # FIXME: define ensemble


################################################################################


def test(X, Y):
    P = predict(X)

    Image.fromarray(P).convert("RGB").save(f"idx{idx}_s{SHAPE[0]}_out1_p.png")
    Image.fromarray(Y).convert("RGB").save(f"idx{idx}_s{SHAPE[0]}_out2_y.png")
    Image.fromarray(X).convert("RGB").save(f"idx{idx}_s{SHAPE[0]}_out3_x.png")

    print(dice_loss_1(P / 255, Y / 255))

    # plt.figure()
    # plt.imshow(P)
    # plt.show()


################################################################################

if __name__ == "__main__":
    if args.train:
        train()
    if args.test:
        _, X_test, _, y_test = get_dataset()
        for idx in range(len(X_test)):
            print(f"=== \033[90m(idx={idx+1}/{len(X_test)})\033[0m ===")
            X, Y = X_test[idx], y_test[idx]
            test(X, Y)
