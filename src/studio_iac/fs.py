"""Atomic, path-explicit file I/O shared by IAC and OpenAPI tooling."""

import json
import os
from pathlib import Path
from typing import Any

_PARTIAL_SUFFIX = ".partial"


class FileReadError(Exception):
    def __init__(self, path: Path, reason: str) -> None:
        self.path = path
        self.reason = reason
        super().__init__(f"cannot read {path}: {reason}")


class FileWriteError(Exception):
    def __init__(self, path: Path, reason: str) -> None:
        self.path = path
        self.reason = reason
        super().__init__(f"cannot write {path}: {reason}")


def resolve_path(raw: str) -> Path:
    """Absolute, user-expanded, symlink-resolved path. Never relative."""
    return Path(raw).expanduser().resolve()


def read_json(path: Path) -> Any:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise FileReadError(path, str(error)) from error
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise FileReadError(path, f"invalid JSON at line {error.lineno}") from error


def write_text_atomic(path: Path, content: str) -> Path:
    """Write via .partial + os.replace so readers never see a truncated file."""
    partial = path.with_name(path.name + _PARTIAL_SUFFIX)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        partial.write_text(content, encoding="utf-8")
        os.replace(partial, path)
    except OSError as error:
        partial.unlink(missing_ok=True)
        raise FileWriteError(path, str(error)) from error
    return path
