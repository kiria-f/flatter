from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    from . import Style, Styles


@dataclass
class StyledText:
    text: str
    style: Style = Styles.EMPTY

    def __len__(self):
        return len(self.text)

    def __iter__(self):
        return iter(self.text)
