from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray

    from framework.core.graphics.styles import Style
StyledLineDefinition = str | list[tuple[str, str]] | tuple[str, dict[int, str]]


class Render:
    text: np.ndarray
    style: np.ndarray

    def __init__(self, text: NDArray[np.str_], styles: NDArray[np.object_]):
        self.text = text
        self.style = styles

    @staticmethod
    def from_lines(lines: list[RenderLine]):
        max_len = max(len(line) for line in lines)
        padded_text_lines = []
        for line in lines:
            pad_len = max_len - len(line)
            if pad_len > 0:
                line = np.append(line.text, [' '] * pad_len)
            padded_text_lines.append(line)
        text = np.vstack(padded_text_lines)
        styles = np.vstack([line.style for line in lines])
        return Render(text, styles)

    @property
    def height(self) -> int:
        return self.text.shape[0]

    @property
    def width(self) -> int:
        return self.text.shape[1]

    @staticmethod
    def empty(width: int, height: int) -> Render:
        text = np.full((height, width), ' ', dtype='U1')
        styles = np.full((height, width), None, dtype=object)
        return Render(text, styles)

    def overlay(self, other: Render, x: int = 0, y: int = 0) -> Render:
        if (
            x < 0
            or y < 0
            or x + other.width > self.width
            or y + other.height > self.height
        ):
            raise ValueError('Overlay dimensions out of bounds')

        new_text = np.copy(self.text)
        new_styles = np.copy(self.style)
        new_text[y : y + other.height, x : x + other.width] = other.text
        new_styles[y : y + other.height, x : x + other.width] = other.style
        return Render(new_text, new_styles)
