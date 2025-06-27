from abc import ABC, abstractmethod
from enum import StrEnum
from typing import override

from app.core.tools import _sgr


class Style(ABC):
    @property
    @abstractmethod
    def _begin(self) -> str:
        pass

    @property
    @abstractmethod
    def _end(self) -> str:
        pass


class StyleMix(Style):
    def __init__(self, *styles: Style):
        self.styles = styles

    @property
    @override
    def _begin(self) -> str:
        return ''.join([style._begin for style in self.styles])

    @property
    @override
    def _end(self) -> str:
        return ''.join([style._end for style in self.styles])


class Foreground(Style):
    class Console(StrEnum):
        BLACK = _sgr(30)
        RED = _sgr(31)
        GREEN = _sgr(32)
        YELLOW = _sgr(33)
        BLUE = _sgr(34)
        MAGENTA = _sgr(35)
        CYAN = _sgr(36)
        WHITE = _sgr(37)

    class ConsoleBright(StrEnum):
        BLACK = _sgr(90)
        RED = _sgr(91)
        GREEN = _sgr(92)
        YELLOW = _sgr(93)
        BLUE = _sgr(94)
        MAGENTA = _sgr(95)
        CYAN = _sgr(96)
        WHITE = _sgr(97)

    class RGB:
        def __init__(self, r: int, g: int, b: int):
            self.r = r
            self.g = g
            self.b = b

        @staticmethod
        def from_hex(hex_color: str):
            color = hex_color.lstrip('#')
            if len(color) == 2:
                color *= 3
            if len(color) == 3:
                color = ''.join([c * 2 for c in color])
            r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
            return Foreground.RGB(r, g, b)

        def __str__(self):
            return _sgr(38, 2, self.r, self.g, self.b)

    def __init__(self, color: str | Console | ConsoleBright | RGB):
        self.color = color

    @property
    @override
    def _begin(self) -> str:
        return str(self.color)

    @property
    @override
    def _end(self) -> str:
        return _sgr(39)


class Background(Style):
    class Console(StrEnum):
        BLACK = _sgr(40)
        RED = _sgr(41)
        GREEN = _sgr(42)
        YELLOW = _sgr(43)
        BLUE = _sgr(44)
        MAGENTA = _sgr(45)
        CYAN = _sgr(46)
        WHITE = _sgr(47)

    class ConsoleBright(StrEnum):
        BLACK = _sgr(100)
        RED = _sgr(101)
        GREEN = _sgr(102)
        YELLOW = _sgr(103)
        BLUE = _sgr(104)
        MAGENTA = _sgr(105)
        CYAN = _sgr(106)
        WHITE = _sgr(107)

    class RGB(Foreground.RGB):
        def __str__(self):
            return _sgr(48, 2, self.r, self.g, self.b)

    def __init__(self, color: str | Console | ConsoleBright):
        self.color = color

    @property
    @override
    def _begin(self) -> str:
        return str(self.color)

    @property
    @override
    def _end(self) -> str:
        return _sgr(49)


class Bold(Style):
    @property
    @override
    def _begin(self) -> str:
        return _sgr(1)

    @property
    @override
    def _end(self) -> str:
        return _sgr(22)


class Italic(Style):
    @property
    @override
    def _begin(self) -> str:
        return _sgr(3)

    @property
    @override
    def _end(self) -> str:
        return _sgr(23)


class Underline(Style):
    @property
    @override
    def _begin(self) -> str:
        return _sgr(4)

    @property
    @override
    def _end(self) -> str:
        return _sgr(24)


class Blink(Style):
    @property
    @override
    def _begin(self) -> str:
        return _sgr(5)

    @property
    @override
    def _end(self) -> str:
        return _sgr(25)


class Inverse(Style):
    @property
    @override
    def _begin(self) -> str:
        return _sgr(7)

    @property
    @override
    def _end(self) -> str:
        return _sgr(27)


class Strikethrough(Style):
    @property
    @override
    def _begin(self) -> str:
        return _sgr(9)

    @property
    @override
    def _end(self) -> str:
        return _sgr(29)
