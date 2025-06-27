from typing import TYPE_CHECKING, override

from app.core.widgets.widget import Widget

if TYPE_CHECKING:
    from app.core.widgets.widget import Render, Widget


class Padding(Widget):
    def __init__(
        self,
        *,
        top: int = 0,
        right: int = 0,
        bottom: int = 0,
        left: int = 0,
        child: Widget,
    ):
        self._top = top
        self._right = right
        self._bottom = bottom
        self._left = left
        self._child = child

    @override
    def _render(self, width: int, height: int) -> Render:
        child_width = width - self._left - self._right
        child_height = height - self._top - self._bottom

        child_render = self._child._render(child_width, child_height)

        r = Render.empty(width, height)
        r.overlay(child_render, self._left, self._top)
        return r
