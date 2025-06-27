from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.render_engine import Render


class Widget(ABC):
    @abstractmethod
    def _render(self, width: int, height: int) -> Render:
        pass
