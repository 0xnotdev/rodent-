from __future__ import annotations

import re
from pathlib import Path

PIN_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[0-9a-f]{40}$")
USES_RE = re.compile(r"^\s*uses:\s*([^\s#]+)", re.MULTILINE)


def main() -> None:
    failures: list[str] = []
    for path in sorted(Path(".github/workflows").glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        for value in USES_RE.findall(text):
            if not PIN_RE.match(value):
                failures.append(f"{path}: unpinned action {value}")
    if failures:
        raise SystemExit("\n".join(failures))


if __name__ == "__main__":
    main()
