from __future__ import annotations

from typing import TYPE_CHECKING, List

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray

    from framework.core.graphics import StyledText


class Canvas:
    text: np.ndarray
    style: np.ndarray

    def __init__(self, text: NDArray[np.str_], style: NDArray[np.object_]):
        assert text.shape == style.shape
        self.text = text
        self.style = style

    @staticmethod
    def from_lines(lines: List[List[StyledText]]):
        canvas_lines = []
        canvas_styles = []
        for line in lines:
            canvas_line = np.array([])
            canvas_style = np.array([])
            for segment in line:
                canvas_line = np.concatenate((canvas_line, np.array(list(segment))))
                canvas_style = np.concatenate((canvas_style, np.full(len(segment), segment.style)))
            canvas_lines.append(canvas_line)
            canvas_styles.append(canvas_style)

        text = np.vstack(canvas_lines)
        styles = np.vstack(canvas_styles)

        return Canvas(text, styles)

    @property
    def height(self) -> int:
        return self.text.shape[0]

    @property
    def width(self) -> int:
        return self.text.shape[1]

    @staticmethod
    def empty(width: int, height: int) -> Canvas:
        text = np.full((height, width), ' ', dtype='U1')
        styles = np.full((height, width), None, dtype=object)
        return Canvas(text, styles)

    def overlay(self, other: Canvas, x: int = 0, y: int = 0) -> Canvas:
        if x < 0:
            x = self.width - other.width + x + 1
        if y < 0:
            y = self.height - other.height + y + 1
        assert x + other.width <= self.width and y + other.height <= self.height, 'Overlay dimensions are out of bounds'

        new_text = np.copy(self.text)
        new_styles = np.copy(self.style)
        new_text[y : y + other.height, x : x + other.width] = other.text
        new_styles[y : y + other.height, x : x + other.width] = other.style
        return Canvas(new_text, new_styles)

    def draw(self):
        pass
