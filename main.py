#!/usr/bin/env python3
"""Copy the news front-page entry image to the output directory.

The entry itself is the single image ``entry.png`` next to this script:
a dense 1024x1024 newspaper front page summarising 24 November 2026
world news, rendered deterministically by ``gen_image.py``. This script
does not regenerate the image — it only copies the finished entry into
the grader's output directory so the entry is runnable as a program.
"""

import os
import shutil
from pathlib import Path

ENTRY = Path(__file__).resolve().parent / "entry.png"


def main() -> None:
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / "entry.png"
    shutil.copyfile(ENTRY, dest)
    print(f"Wrote {dest} ({dest.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
