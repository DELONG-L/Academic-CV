#!/usr/bin/env python3
"""Package current English and Chinese PDFs with editable source and licenses."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import zipfile

from artifacts import ROOT, cache_directories, require_current

EXCLUDED_DIRECTORIES = {".git", "_build", ".venv", "__pycache__"}
EXCLUDED_SUFFIXES = {".aux", ".bbl", ".bcf", ".blg", ".fdb_latexmk", ".fls",
                     ".log", ".out", ".xdv", ".cvmeta", ".rng", ".zip"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "academic-cv.zip")
    args = parser.parse_args()
    try:
        require_current()
        caches = cache_directories()
        output = args.output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_name(output.name + ".tmp")
        try:
            with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for path in sorted(ROOT.rglob("*")):
                    relative = path.relative_to(ROOT)
                    if not path.is_file() or any(part in EXCLUDED_DIRECTORIES for part in relative.parts):
                        continue
                    if any(part.startswith(".academic-cv-") for part in relative.parts):
                        continue
                    if any(cache == path or cache in path.parents for cache in caches):
                        continue
                    if path in {output, temporary} or path.suffix in EXCLUDED_SUFFIXES or path.name == ".DS_Store":
                        continue
                    if path.name.endswith(".run.xml"):
                        continue
                    archive.write(path, relative.as_posix())
            with zipfile.ZipFile(temporary) as archive:
                if archive.testzip() is not None:
                    raise RuntimeError("ZIP integrity check failed.")
            temporary.replace(output)
        finally:
            if temporary.exists():
                temporary.unlink()
        print(f"Packaged {output}")
    except (RuntimeError, OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
