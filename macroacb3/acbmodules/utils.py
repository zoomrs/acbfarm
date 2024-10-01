import cv2
from ctypes import windll, create_unicode_buffer
from typing import Union
import numpy as np
from enum import Enum

class RGB:
    def __init__(self, red=0, green=0, blue=0):
        self.r = red
        self.g = green
        self.b = blue

class Coords2D:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    def __str__(self):
        return f"({self.x}, {self.y})"

class FramePixel:
    def __init__(self, coord: Coords2D, color: RGB):
        self.coord = coord
        self.color = color

class Region:
    def __init__(self, startx, starty, endx, endy):
        self.startx = startx
        self.endx = endx
        self.starty = starty
        self.endy = endy

    def center(self) -> Coords2D:
        centerx = (self.startx + self.endx) / 2
        centery = (self.starty + self.endy) / 2
        return Coords2D(centerx, centery)

class Challenges(Enum):
    heroiclaststand, pridespower, grandrescue = 1, 2, 3
    sagestrial, innerdemon, speedoflighting = 4, 5, 6
    vengeancepath, slayerswill = 7, 8

class Maps:
    class Indents:
        TPmenu = FramePixel(Coords2D(921, 269), RGB(163, 4, 178))
        hidebattle = FramePixel(Coords2D(1307, 987), RGB(255, 255, 255))
        challengeui = FramePixel(Coords2D(913, 270), RGB(255, 105, 103))
    class Buttons:
        acceptdialog = Coords2D(863, 830)
        recusedialog = Coords2D(1052, 830)
        teleporttoarena = Coords2D(1143, 540)
        takeabreak = Coords2D(811, 837)
        teleport = Coords2D(138, 630)
        enablehardmode = Coords2D(1122, 753)
        enterchallenge = Coords2D(987, 753)

    challengesmap = {  # scroll: positions
        0: {
            Challenges.heroiclaststand: Coords2D(748, 472),
            Challenges.pridespower: Coords2D(748, 588),
            Challenges.grandrescue: Coords2D(748, 705),
        },
        2: {
            Challenges.sagestrial: Coords2D(748, 506),
            Challenges.innerdemon: Coords2D(748, 634),
            Challenges.speedoflighting: Coords2D(748, 735),
        },
        4: {
            Challenges.vengeancepath: Coords2D(748, 601),
            Challenges.slayerswill: Coords2D(748, 716),
        }
    }

    closebuttons = {
        "deck": (FramePixel(Coords2D(583, 305), RGB(175, 18, 226)), Coords2D(1431, 334)),
        "backpack": (FramePixel(Coords2D(562, 320), RGB(23, 221, 139)), Coords2D(1342, 349)),
        "quests": (FramePixel(Coords2D(622, 255), RGB(18, 121, 226)), Coords2D(1280, 291)),
        "battlepass": (FramePixel(Coords2D(578, 280), RGB(244, 218, 0)), Coords2D(1372, 324)),
        "teleports": (FramePixel(Coords2D(617, 291), RGB(240, 83, 82)), Coords2D(1283, 290)),
        "rewards": (FramePixel(Coords2D(1263, 325), RGB(38, 38, 38)), Coords2D(1263, 337)),
        "challenges": (FramePixel(Coords2D(627, 256), RGB(255, 106, 29)), Coords2D(1284, 290))
    }

class Regions:
    bye = Region(968, 807, 1136, 850)
    gameplaypaused = Region(881, 498, 1040, 522)
    areatp = Region(918, 341, 997, 359),
    enterchallenge = Region(898, 738, 1077, 796)

class Templates:
    areastp = cv2.imread("images/areastp.png")
    bye = cv2.imread("images/bye.png")
    enterchallenge = cv2.imread("images/enterchallenge.png")
    gameplaypaused = cv2.imread("images/gameplaypaused.png")

class LogColor:
    red = "\033[0;31m"
    green = "\033[0;32m"
    yellow = "\033[0;33m"

async def getscreenpixelcolordiff(frame, position: Coords2D, color: RGB):
    return (np.array([color.r, color.g, color.b]) - frame[position.y, position.x]).mean()

async def istemplatevisible(frame, template, similiarity: float = 0.88, region = Union[Region, None]) -> (bool, Coords2D):
    if not isinstance(region, Region):
        comparison = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(comparison >= similiarity)
    else:
        frameregion = frame[region.starty:region.endy, region.startx:region.endx]
        comparison = cv2.matchTemplate(frameregion, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(comparison >= similiarity)

    position = Coords2D(-1, -1)
    positions = list(zip(*loc[::-1]))
    if positions:
        centerx = sum(pos[0] for pos in positions) // len(positions)
        centery = sum(pos[1] for pos in positions) // len(positions)
        position.x = centerx
        position.y = centery
    else:
        return False, None
    position.x, position.y = int(position.x), int(position.y)
    if not isinstance(region, Region):
        return True, Coords2D(position.x, position.y)

    return True, Coords2D(position.x+region.startx, position.y+region.starty)

async def acblog(message: str, color: LogColor = LogColor.green):
    print(f"{color}{message}\033[0m")

async def isinroblox():
    window = create_unicode_buffer(7)
    windll.user32.GetWindowTextW(windll.user32.GetForegroundWindow(), window, 7)
    if not window.value == "Roblox":
        inroblox = False
    else:
        inroblox = True
    return inroblox