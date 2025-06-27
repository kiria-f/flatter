from typing import Any


class VariableValue:
    def __init__(self, value: Any):
        self._value = value
        self._changed = True

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        if self._value != value:
            self._changed = True
            self._value = value

    @property
    def changed(self) -> bool:
        return self._changed

    def _reset(self) -> None:
        self._changed = False

    def invalidate(self) -> None:
        self._changed = True


class Variables:
    def __init__(self):
        self._variables: dict[str, VariableValue] = {}

    def _raw_get(self, key: str) -> VariableValue | None:
        return self._variables.get(key)

    def get(self, key: str) -> Any | None:
        var = self._variables.get(key)
        return var if var is None else var.value

    def set(self, key: str, value: Any) -> None:
        if key not in self._variables:
            self._variables[key] = VariableValue(value)
        else:
            self._variables[key].value = value

    def _reset(self) -> None:
        for variable in self._variables.values():
            variable._reset()

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __contains__(self, key: object) -> bool:
        return key in self._variables
