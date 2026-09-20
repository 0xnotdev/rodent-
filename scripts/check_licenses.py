from __future__ import annotations

import tomllib
from pathlib import Path

# CP-00 dependency/license allowlist. Each locked runtime/dev transitive dependency
# must be deliberately named here so new or unknown dependencies fail closed.
ALLOWED_LICENSES_BY_PACKAGE = {
    "annotated-types": {"MIT"},
    "click": {"BSD-3-Clause"},
    "colorama": {"BSD-3-Clause"},
    "coverage": {"Apache-2.0"},
    "iniconfig": {"MIT"},
    "markdown-it-py": {"MIT"},
    "mdurl": {"MIT"},
    "mypy": {"MIT"},
    "mypy-extensions": {"MIT"},
    "packaging": {"Apache-2.0 OR BSD-2-Clause"},
    "pluggy": {"MIT"},
    "proof": {"Apache-2.0"},
    "pydantic": {"MIT"},
    "pydantic-core": {"MIT"},
    "pygments": {"BSD-2-Clause"},
    "pytest": {"MIT"},
    "rfc8785": {"Apache-2.0"},
    "rich": {"MIT"},
    "ruff": {"MIT"},
    "shellingham": {"ISC"},
    "typer": {"MIT"},
    "typing-extensions": {"Python-2.0"},
}

LICENSE_BY_PACKAGE = {
    "annotated-types": "MIT",
    "click": "BSD-3-Clause",
    "colorama": "BSD-3-Clause",
    "coverage": "Apache-2.0",
    "iniconfig": "MIT",
    "markdown-it-py": "MIT",
    "mdurl": "MIT",
    "mypy": "MIT",
    "mypy-extensions": "MIT",
    "packaging": "Apache-2.0 OR BSD-2-Clause",
    "pluggy": "MIT",
    "proof": "Apache-2.0",
    "pydantic": "MIT",
    "pydantic-core": "MIT",
    "pygments": "BSD-2-Clause",
    "pytest": "MIT",
    "rfc8785": "Apache-2.0",
    "rich": "MIT",
    "ruff": "MIT",
    "shellingham": "ISC",
    "typer": "MIT",
    "typing-extensions": "Python-2.0",
}


def main() -> None:
    lock = tomllib.loads(Path("uv.lock").read_text(encoding="utf-8"))
    locked_names = {package["name"] for package in lock["package"]}
    failures: list[str] = []
    for name in sorted(locked_names):
        if name not in ALLOWED_LICENSES_BY_PACKAGE:
            failures.append(f"unknown dependency: {name}")
            continue
        license_id = LICENSE_BY_PACKAGE.get(name)
        if license_id not in ALLOWED_LICENSES_BY_PACKAGE[name]:
            failures.append(f"disallowed license for {name}: {license_id or 'UNKNOWN'}")
    missing = sorted(set(ALLOWED_LICENSES_BY_PACKAGE) - locked_names)
    failures.extend(f"allowlisted dependency not locked: {name}" for name in missing)
    if failures:
        raise SystemExit("\n".join(sorted(failures)))
    print(f"license allowlist ok: {len(locked_names)} locked packages")


if __name__ == "__main__":
    main()
