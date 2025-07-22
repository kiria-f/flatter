from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from framework.core import Element


class Widget(ABC):
    key: str | None

    def __init__(self, key: str | None) -> None:
        self.key = key

    @abstractmethod
    def create_element(self) -> Element:
        pass

    @abstractmethod
    def can_update(self, old_widget: Widget) -> bool:
        pass
