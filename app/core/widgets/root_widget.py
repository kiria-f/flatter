import os
from typing import TYPE_CHECKING

from app.core.widgets.widget import Widget

if TYPE_CHECKING:
    from app.core.widgets.widget import Render


class RootWidget(Widget):
    def __init__(self, *, child: Widget):
        self._child = child

    def _render(self) -> Render:  # type: ignore
        self._width, self._height = os.get_terminal_size()
        return self._child._render(self._width, self._height)
