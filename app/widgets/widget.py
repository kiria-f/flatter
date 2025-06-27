from abc import ABC
from enum import Enum


class Widget(ABC):
    class Geometry:
        class Position(Enum):
            ABSOLUTE = 0b0
            RELATIVE = 0b1

        class HorizontalAlignment(Enum):
            LEFT = 0x0
            CENTER = 0x1
            RIGHT = 0x2

        class VerticalAlignment(Enum):
            TOP = 0x00
            CENTER = 0x10
            BOTTOM = 0x20

        def __init__(
            self,
            x: int,
            y: int,
            width: int,
            height: int,
            position: Position = Position.RELATIVE,
            alignment: HorizontalAlignment | VerticalAlignment = HorizontalAlignment.LEFT | VerticalAlignment.TOP,
        ):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.position = position
            self.alignment = alignment

    dependencies: list[str]
    geometry: Geometry | None

    def _redraw():
        pass
