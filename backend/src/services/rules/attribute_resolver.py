from typing import Any


class _Missing:
    _instance: "_Missing | None" = None

    def __new__(cls) -> "_Missing":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "<MISSING>"

    def __bool__(self) -> bool:
        return False


MISSING: Any = _Missing()


def resolve_path(obj: Any, path: str) -> Any:
    if not path:
        return MISSING

    current = obj
    for part in path.split("."):
        if current is MISSING or current is None:
            return MISSING

        if part == "count" and isinstance(current, list | tuple):
            current = len(current)
            continue

        if isinstance(current, dict):
            if part in current:
                current = current[part]
                continue
            return MISSING

        if hasattr(current, part):
            current = getattr(current, part)
            continue

        return MISSING

    return current
