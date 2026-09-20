from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_coverage.py coverage.xml")
    path = Path(sys.argv[1])
    root = ET.parse(path).getroot()
    if root.tag != "coverage":
        raise SystemExit("not a coverage XML file")
    if float(root.attrib.get("line-rate", "0")) <= 0:
        raise SystemExit("coverage XML has no covered lines")


if __name__ == "__main__":
    main()
