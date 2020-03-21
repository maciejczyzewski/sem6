import matplotlib.pyplot as plt
import numpy as np
import unidecode
import csv
import re


def slugify(text):
    text = unidecode.unidecode(text).lower()
    text = re.sub(r"[\W_]+", "-", text)
    if text[-1] == "-":
        return text[0:-1]
    return text


class figure:
    def __init__(self, name=None, prefix=None):
        self.name = name
        self.prefix = prefix

    def __enter__(self):
        print("--- FIGURE ---")
        print(f"`{self.name}`")
        plt.cla()
        plt.title(self.name)

    def __exit__(self, x, y, z):
        print("--- SAVE ---")
        figure_prefix = "figure-"
        if self.prefix is not None:
            figure_prefix += f"{str(self.prefix)}-"
        fig.savefig(f"raport/{figure_prefix}{slugify(self.name)}.pdf")


def fill_between(X, Y, color="blue", alpha=0.05, factor=1):
    sigma = factor * np.array(Y).std(axis=0)  # ls = '--'
    ax.fill_between(X, Y + sigma, Y - sigma, facecolor=color, alpha=alpha)


# (1) better style
plt.style.use(["science", "ieee"])

fig, ax = plt.subplots()
ax.autoscale(tight=True)


################################################################################

# R: liczba detektorów zmienia się od 90 do 720 z krokiem 90
#    (x * 90)
# A: liczba skanów zmienia się od 90 do 720 z krokiem 90
#    (180 / (x * 90))
# L: rozpiętość wachlarza zmienia się od 45 do 270 stopni z krokiem 45 stopni
#    (x * 45) / np.pi

################################################################################

CONFIG = {
    "path": "data/Shepp_logan.jpg",
    "shape": (320, 320),
    "alpha": 180 / (2 * 90),
    "rays": 2 * 90,
    "l": 4 * 45 / np.pi,
    "filtered": True,
}

rp, rn = 90, 8
ap, an = 90, 8
lp, ln = 45, 6

R1Y = [
    0.1190555626450787,
    0.10362224161176702,
    0.0982745449755499,
    0.0997357482593574,
    0.10078430888046792,
    0.10139318976687542,
    0.10184263635134466,
    0.10309777497858848,
]

A1Y = [
    0.116329421329591,
    0.10362224161176702,
    0.0999417937231325,
    0.0977067154794791,
    0.09835977341644636,
    0.09679339403408399,
    0.09643469029343751,
    0.0964892736743682,
]

L1Y = [
    0.25772221584635346,
    0.2634496794196945,
    0.21783810900055212,
    0.10362224161176702,
    0.1027079277644246,
    0.10798060784212034,
]

R1X = [90, 180, 270, 360, 450, 540, 630, 720]
A1X = [90, 180, 270, 360, 450, 540, 630, 720]
L1X = [45, 90, 135, 180, 225, 270]

with figure("rays (alpha=180, l=180)", prefix=1):
    plt.plot(R1X, R1Y, color="darkred")

    fill_between(R1X, R1Y, color="red", factor=0.5, alpha=0.1)

    plt.ylabel("RMSE")
    plt.xlabel("value")


with figure("alpha (rays=180, l=180)", prefix=1):
    plt.plot(A1X, A1Y, color="darkblue")

    fill_between(A1X, A1Y, color="blue", factor=0.5, alpha=0.1)

    plt.ylabel("RMSE")
    plt.xlabel("value")


with figure("l (alpha=180, rays=180)", prefix=1):
    plt.plot(L1X, L1Y, color="darkgreen")

    fill_between(L1X, L1Y, color="green", factor=0.5, alpha=0.1)

    plt.ylabel("RMSE")
    plt.xlabel("value")

################################################################################

CONFIG = {
    "path": "data/Shepp_logan.jpg",
    "shape": (600, 600),
    "alpha": 0.5,
    "rays": 1000,
    "l": 600 / np.pi,
    "filtered": True,
}

rp, rn = 200, 8
ap, an = 90, 8
lp, ln = 45, 20

R2Y = [
    0.14311898575197346,
    0.10988676188677274,
    0.09565383786580678,
    0.08920681026258603,
    0.08556099048086623,
    0.08216739360398152,
    0.07957054719941416,
    0.07752871364111938,
]

A2Y = [
    0.11676531050642112,
    0.096953499821459,
    0.0882596512034773,
    0.08556099048086623,
    0.08270083151635209,
    0.08088206284680526,
    0.07985736676250449,
    0.07970708695938904,
]

L2Y = [
    0.2356588635946367,
    0.2362811024129519,
    0.1839094901962631,
    0.10003261932697888,
    0.08515020197507045,
    0.08021881694198375,
    0.07765227043859342,
    0.07733985988748446,
    0.07880985994442159,
    0.08099915875008472,
    0.08228603804297517,
    0.08365646127323181,
    0.08562917332783337,
    0.08657155473500237,
    0.0885090387756539,
    0.09016295407788132,
    0.0910302338239611,
    0.0922765647924996,
    0.0940388284349591,
    0.09516784857568857,
]


R2X = [200, 400, 600, 800, 1000, 1200, 1400, 1600]
A2X = [90, 180, 270, 360, 450, 540, 630, 720]
L2X = [
    45,
    90,
    135,
    180,
    225,
    270,
    315,
    360,
    405,
    450,
    495,
    540,
    585,
    630,
    675,
    720,
    765,
    810,
    855,
    900,
]

with figure("rays (alpha=360, l=600)", prefix=2):
    plt.plot(R2X, R2Y, color="darkred")

    fill_between(R2X, R2Y, color="red", factor=0.5, alpha=0.1)

    plt.ylabel("RMSE")
    plt.xlabel("value")


with figure("alpha (rays=1000, l=600)", prefix=2):
    plt.plot(A2X, A2Y, color="darkblue")

    fill_between(A2X, A2Y, color="blue", factor=0.5, alpha=0.1)

    plt.ylabel("RMSE")
    plt.xlabel("value")


with figure("l (alpha=360, rays=1000)", prefix=2):
    plt.plot(L2X, L2Y, color="darkgreen")

    fill_between(L2X, L2Y, color="green", factor=0.5, alpha=0.1)

    plt.ylabel("RMSE")
    plt.xlabel("value")
