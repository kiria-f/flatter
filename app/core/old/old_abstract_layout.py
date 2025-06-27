from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.core.listener import Listener
    from app.core.render_engine import StyledLine
    from app.core.variable import Variables, VariableValue


class AbstractLayout(ABC):
    def __init__(
        self,
        *,
        id: str | None = None,
        variables: dict[str, Any] | None = None,
        depends_on: list[str] | None = None,
        listener: Listener | None = None,
        width: int | None = None,
        height: int | None = None,
        children: list[Child] | None = None,
    ) -> None:
        self._parent: AbstractLayout | None = None
        self._id = id
        self._children: list[Child] = []
        self._variables = Variables()
        if variables is not None:
            for key, value in variables.items():
                self._variables[key] = value
        self._depends_on = depends_on or []
        self._listener = listener
        if self._listener is not None:
            self._listener.widget = self
        self._width = width
        self._height = height
        if children is not None:
            self.add_children(children)
        self._cache: list[StyledLine] | None = None

    def _raw_lookup(self, variable: str) -> VariableValue | None:
        if variable in self._variables:
            return self._variables._raw_get(variable)
        if self._parent is not None:
            return self._parent._raw_lookup(variable)
        return None

    @property
    def fixed_width(self) -> bool:
        return self._width is not None

    @property
    def fixed_height(self) -> bool:
        return self._height is not None

    @property
    def width(self) -> int:
        if self._width is not None:
            return self._width
        else:
            return self.lookup('width')

    @property
    def height(self) -> int:
        if self._height is not None:
            return self._height
        else:
            return self.lookup('height')

    def add_children(self, children: list[Child]) -> None:
        for child in children:
            child.widget._parent = self
            self._children.append(child)

    def lookup(self, variable: str) -> Any:
        if variable in self._variables:
            return self._variables[variable]
        if self._parent is not None:
            return self._parent.lookup(variable)
        return None

    def override(self, variable: str, value: Any) -> None:
        self._variables[variable] = value

    def update(self, variable, value: Any) -> None:
        var = self._raw_lookup(variable)
        if var is not None:
            var.value = value
        else:
            self.override(variable, value)

    def render(self) -> list[StyledLine]:
        for child in self._children:
            child_render = child.widget.render()


# class Child:
#     def __init__(
#         self,
#         widget: AbstractLayout,
#         *,
#         horizontal_alignment: HorizontalAlignment | None = None,
#         vertical_alignment: VerticalAlignment | None = None,
#         left_margin: int | None = None,
#         right_margin: int | None = None,
#         horizontal_margins: int | None = None,
#         top_margin: int | None = None,
#         bottom_margin: int | None = None,
#         vertical_margins: int | None = None,
#         margins: int | None = None,
#         x: Coordinate | None = None,
#         y: Coordinate | None = None,
#         runtime_validate: bool = True,
#     ) -> None:
#         self.widget = widget
#         self.vertical_alignment = vertical_alignment
#         self.horizontal_alignment = horizontal_alignment
#         self.left_margin = left_margin
#         self.right_margin = right_margin
#         self.horizontal_margins = horizontal_margins
#         self.top_margin = top_margin
#         self.bottom_margin = bottom_margin
#         self.vertical_margins = vertical_margins
#         self.margins = margins
#         self.x = x
#         self.y = y
#         if runtime_validate:
#             ChildValidator.validate(self)


# class ChildValidator:
#     @staticmethod
#     def validate(child: Child) -> None:
#         if child.horizontal_alignment is None:
#             assert child.left_margin is None, 'Left margin cannot be set without horizontal alignment'
#             assert child.right_margin is None, 'Right margin cannot be set without horizontal alignment'
#             assert child.horizontal_margins is None, 'Horizontal margins cannot be set without horizontal alignment'
#             assert child.margins is None, 'Margins cannot be set without horizontal alignment'
#             assert child.x is not None, 'X position must be set without horizontal alignment'
#         else:
#             assert child.x is None, 'X position cannot be set with horizontal alignment'
#         if child.vertical_alignment is None:
#             assert child.top_margin is None, 'Top margin cannot be set without vertical alignment'
#             assert child.bottom_margin is None, 'Bottom margin cannot be set without vertical alignment'
#             assert child.vertical_margins is None, 'Vertical margins cannot be set without vertical alignment'
#             assert child.margins is None, 'Margins cannot be set without vertical alignment'
#             assert child.y is not None, 'Y position must be set without vertical alignment'
#         else:
#             assert child.y is None, 'Y position cannot be set with vertical alignment'
#         if child.widget._width is None:
#             assert child.horizontal_alignment is None, 'Horizontal alignment cannot be set without width'
#             assert child.x is None, 'X position cannot be set without width'
#         else:
#             assert child.horizontal_alignment is not None or child.x is not None, 'X position or horizontal alignment must be set with width'
#         if child.widget._height is None:
#             assert child.vertical_alignment is None, 'Vertical alignment cannot be set without height'
#             assert child.y is None, 'Y position cannot be set without height'
#         else:
#             assert child.vertical_alignment is not None or child.y is not None, 'Y position or vertical alignment must be set with height'
