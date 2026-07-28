"""Static evidence boundary checks for primary image processing code."""

from __future__ import annotations

import ast
from pathlib import Path
import re
from typing import Iterable


def scan_primary_lane(
    package_root: str | Path,
    forbidden: Iterable[str],
    *,
    include: Iterable[str] | None = None,
) -> list[str]:
    root = Path(package_root)
    if not root.is_dir():
        return [f"PACKAGE_MISSING:{root}"]
    patterns = {
        token: re.compile(rf"(?<![a-z0-9]){re.escape(token.lower())}(?![a-z0-9])")
        for token in forbidden
    }
    hits: list[str] = []
    if include is None:
        paths = sorted(root.rglob("*.py"))
    else:
        paths = []
        resolved_root = root.resolve()
        for relative in sorted(set(include)):
            path = (root / relative).resolve()
            if resolved_root not in path.parents or not path.is_file():
                hits.append(f"PRIMARY_MODULE_MISSING_OR_OUTSIDE:{relative}")
                continue
            paths.append(path)

    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        values: list[tuple[int, str]] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                values.extend((node.lineno, item.name) for item in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                values.append((node.lineno, node.module))
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                values.append((getattr(node, "lineno", 0), node.value))
            elif isinstance(node, ast.Call):
                direct = isinstance(node.func, ast.Name) and node.func.id in {
                    "__import__",
                    "eval",
                    "exec",
                }
                imported = (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr == "import_module"
                )
                if direct or imported:
                    hits.append(
                        f"{path.relative_to(root)}:{getattr(node, 'lineno', 0)}:DYNAMIC_IMPORT"
                    )
        for line_number, value in values:
            lowered = value.lower()
            for token, pattern in patterns.items():
                if pattern.search(lowered):
                    hits.append(f"{path.relative_to(root)}:{line_number}:{token}")
    return hits
