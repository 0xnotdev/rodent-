from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_sbom.py SBOM.json")
    path = Path(sys.argv[1])
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("bomFormat") != "CycloneDX":
        raise SystemExit("SBOM is not CycloneDX")
    if not str(data.get("specVersion", "")).startswith("1.5"):
        raise SystemExit("SBOM is not CycloneDX 1.5")
    components = data.get("components")
    if not isinstance(components, list) or not components:
        raise SystemExit("SBOM has no components")


if __name__ == "__main__":
    main()
