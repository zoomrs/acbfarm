import asyncio
from asyncio import sleep
from ctypes import windll as windll, Structure, Union, sizeof, byref
from acbmodules.utils import Coords2D, isinroblox
import ctypes.wintypes as wintypes


class _MOUSEINPUT(Structure):
    _fields_ = (("dx", wintypes.LONG), ("dy", wintypes.LONG),
                ("mousedata", wintypes.DWORD), ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("extrainfo", wintypes.WPARAM))

class _KEYBOARDINPUT(Structure):
    _fields_ = (("virtualkey", wintypes.WORD), ("scan", wintypes.WORD),
                ("flags", wintypes.DWORD), ("time", wintypes.DWORD),
                ("extrainfo", wintypes.WPARAM))

    def __init__(self, *args, **kwds):
        super(_KEYBOARDINPUT, self).__init__(*args, **kwds)
        if not self.flags & 0x0004:
            self.scan = windll.user32.MapVirtualKeyExW(self.virtualkey, 0, 0)

class _INPUT(Structure):
    class __INPUT(Union):
        _fields_ = (("keyboardinput", _KEYBOARDINPUT),
                    ("mouseinput", _MOUSEINPUT))

    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", __INPUT))


class Mouse:
    class Button:
        LEFT, RIGHT = 1, 2

    @staticmethod
    async def position() -> Coords2D:
        pos = wintypes.POINT()
        windll.user32.GetCursorPos(byref(pos))
        return Coords2D(pos.x, pos.y)

    @staticmethod
    async def move(x: int, y: int) -> bool:
        if not (await isinroblox()):
            return False
        windll.user32.SetCursorPos(x, y)
        inputstruct = _INPUT(type=0, mouseinput=_MOUSEINPUT(1, 1, 0, 0x0001, 0, 0))
        windll.user32.SendInput(1, byref(inputstruct), sizeof(inputstruct))
        return True

    @staticmethod
    async def movev2(position: Coords2D) -> bool:
        await Mouse.move(position.x, position.y)
        return True

    @staticmethod
    async def click(x: int, y: int, button: Button = Button.LEFT) -> bool:
        if not (await isinroblox()):
            return False
        await Mouse.move(x, y)

        clickdown = _INPUT(type=0, mouseinput=_MOUSEINPUT(1, 1, 0, 0x0002 if button == Mouse.Button.LEFT else 0x0008, 0, 0))
        windll.user32.SendInput(1, byref(clickdown), sizeof(clickdown))

        clickup = _INPUT(type=0, mouseinput=_MOUSEINPUT(1, 1, 0, 0x0004 if button == Mouse.Button.LEFT else 0x0010, 0, 0))
        windll.user32.SendInput(1, byref(clickup), sizeof(clickup))
        return True

    @staticmethod
    async def clickv2(position: Coords2D, button: Button = Button.LEFT) -> bool:
        return await Mouse.click(position.x, position.y, button)

    @staticmethod
    async def scroll(times: int, direction: str = "down") -> bool:
        if not (await isinroblox()):
            return False
        for i in range(times):
            await asyncio.sleep(0.002)
            windll.user32.mouse_event(0x0800, 0, 0, -120 if direction == "down" else 120, 0)
        return True

class Keyboard:
    class Key: # https://learn.microsoft.com/pt-br/windows/win32/inputdev/virtual-key-codes
        A, E, SPACEBAR = 0x41, 0x45, 0x20
        W, S, D = 0x57, 0x53, 0x44
        J = 0x4A

    @staticmethod
    async def presskey(key: Key, duration: float = 0.1) -> bool:
        if not (await isinroblox()):
            return False
        pressdown = _INPUT(type=1, keyboardinput=_KEYBOARDINPUT(virtualkey=key))
        windll.user32.SendInput(1, byref(pressdown), sizeof(pressdown))

        await sleep(duration)

        pressup = _INPUT(type=1, keyboardinput=_KEYBOARDINPUT(virtualkey=key, flags=0x0002))
        windll.user32.SendInput(1, byref(pressup), sizeof(pressup))
        return True