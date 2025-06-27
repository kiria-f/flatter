from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from app.core.layouts.old_abstract_layout import AbstractLayout

if TYPE_CHECKING:
    from app.core.listener import Listener
    from app.core.render_engine import StyledLine


class DataBox(AbstractLayout):
    def __init__(
        self,
        *,
        renderer: Callable[[DataBox, int, int], list[StyledLine]],
        id: str | None = None,
        variables: dict[str, Any] | None = None,
        depends_on: list[str] | None = None,
        listener: Listener | None = None,
        width: int | None = None,
        height: int | None = None,
        children: list[Child] | None = None,
    ):
        super().__init__(id=id, variables=variables, depends_on=depends_on, listener=listener, width=width, height=height, children=children)
        self._renderer = renderer

    def _render(self, width: int, height: int) -> list[StyledLine]:
        return self._renderer(self, width, height)
