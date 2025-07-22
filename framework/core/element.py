from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from framework.core import RenderObject, Widget


class Element:
    def __init__(self, widget: Widget):
        self.widget = widget
        self._children: List[Element] = []
        self.parent: Optional[Element] = None
        self._render_object: Optional[RenderObject] = None

    def mount(self, parent: Optional['Element']):
        self.parent = parent
        if parent is not None:
            parent._children.append(self)
        self._render_object = self.create_render_object()
        self._render_object.element = self

    def unmount(self):
        if self.parent is not None and self in self.parent._children:
            self.parent._children.remove(self)
        self.parent = None
        if self._render_object is not None:
            self._render_object.element = None
            self._render_object = None

    def update(self, new_widget: Widget):
        if not self.widget.can_update(new_widget):
            self.unmount()
            new_element = new_widget.create_element()
            new_element.mount(self.parent)
            return new_element

        self.widget = new_widget
        if self._render_object is not None:
            self._render_object.update(new_widget)
        return self

    @abstractmethod
    def create_render_object(self) -> RenderObject:
        pass
