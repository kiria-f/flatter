from __future__ import annotations

from pydantic.dataclasses import dataclass


def _csi(sign: str, *args: int) -> str:
    return f'\033[{";".join(map(str, args)) if args else ""}{sign}'


def _sgr(*args: int) -> str:
    return _csi('m', *args)


@dataclass(frozen=True, slots=True)
class Style:
    begin: str
    end: str

    @staticmethod
    def mix(*styles: Style) -> Style:
        return Style(
            ''.join(style.begin for style in styles),
            ''.join(style.end for style in styles),
        )

    def mix_with(self, other: Style) -> Style:
        return Style.mix(self, other)


def _meta_colors(bright: int, bg: bool):
    base = 30 + int(bright) * 60 + int(bg) * 10
    end = 39 + int(bg) * 10

    def construct(add_code: int) -> Style:
        return Style(_sgr(base + add_code), _sgr(end))

    class MetaColor:
        BLACK = construct(0)
        RED = construct(1)
        GREEN = construct(2)
        YELLOW = construct(3)
        BLUE = construct(4)
        MAGENTA = construct(5)
        CYAN = construct(6)
        WHITE = construct(7)

    return MetaColor


def _meta_rgb(fg: bool):
    class MetaRGB:
        @staticmethod
        def from_rgb(r: int, g: int, b: int):
            return Style(_sgr((38 if fg else 48), 2, r, g, b), _sgr(39 if fg else 49))

        @staticmethod
        def from_hex(hex_color: str):
            color = hex_color.lstrip('#')
            if len(color) == 2:
                color *= 3
            if len(color) == 3:
                color = ''.join([c * 2 for c in color])
            r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
            return MetaRGB.from_rgb(r, g, b)

    return MetaRGB


class Styles:
    class Foreground:
        Console = _meta_colors(False, False)
        ConsoleBright = _meta_colors(True, False)
        RGB = _meta_rgb(False)

    class Background:
        Console = _meta_colors(False, True)
        ConsoleBright = _meta_colors(True, True)
        RGB = _meta_rgb(True)

    EMPTY = Style('', '')
    BOLD = Style(_sgr(1), _sgr(22))
    ITALIC = Style(_sgr(3), _sgr(23))
    UNDERLINE = Style(_sgr(4), _sgr(24))
    BLINK = Style(_sgr(5), _sgr(25))
    INVERSE = Style(_sgr(7), _sgr(27))
    STRIKETHROUGH = Style(_sgr(9), _sgr(29))
