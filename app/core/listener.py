from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from app.core.input_processor import AnyKey
    from app.core.layouts.old_abstract_layout import AbstractLayout


class Trigger:
    def __init__(self, rule: Callable[[AnyKey], None], action: Callable[[AbstractLayout, AnyKey], None]):
        self.rule = rule
        self.action = action


class Listener:
    def __init__(self, triggers: list[Trigger]):
        self.triggers = triggers
        self.widget: AbstractLayout | None = None
