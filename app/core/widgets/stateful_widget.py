from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.render_engine import Render
    from app.core.widgets.widget import Widget


class StatefulWidget(Widget, ABC):
    def __init__(self) -> None:
        self.needs_build = True

    @abstractmethod
    def _render(self, width: int, height: int) -> Render:
        if self.needs_build:
            self.needs_build = False
            return self.build()._render(width, height)

    @abstractmethod
    def build(self) -> Widget:
        pass
