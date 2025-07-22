from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from framework.core.concepts import Position, SizeBox

if TYPE_CHECKING:
    from framework.core.element import Element
    from framework.core.widget import Widget


class RenderObject(ABC):
    """Базовый класс для всех рендер-объектов."""

    def __init__(self):
        self.element: Optional[Element] = None
        self._constraints: Optional[SizeBox] = None
        self._size: Optional[SizeBox] = None
        self._position: Optional[Position] = None

    @abstractmethod
    def layout(self, constraints: SizeBox):
        """Вычисляет layout рендер-объекта в заданных ограничениях."""
        pass

    # @abstractmethod
    # def render(self) -> Canvas:
    #     """Отрисовывает рендер-объект на заданном холсте."""
    #     pass

    @abstractmethod
    def update(self, new_widget: Widget):
        """Обновляет рендер-объект при изменении виджета."""
        pass
