#!/usr/bin/env python3
"""Validate publication metadata using Biber's parser, without changing the .bib."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from artifacts import ROOT, normalize_uri, validate_uri

NS = {"b": "http://biblatex-biber.sourceforge.net/biblatexml"}


def validate_publications(paths: list[Path], destination: Path, env: dict | None = None) -> int:
    environment = env or os.environ.copy()
    biber = shutil.which("biber", path=environment.get("PATH"))
    if not biber:
        raise RuntimeError("Biber was not found. Add TeX Live to PATH or set TEXLIVE_BIN.")
    destination.mkdir(parents=True, exist_ok=True)
    seen_dois = {}
    seen_keys = set()
    count = 0
    for index, source in enumerate(paths):
        xml_path = destination / f"publications-{index}.xml"
        command = [
            biber, "--tool", "--noconf", "--output-resolve",
            "--no-bltxml-schema", "--output-format=biblatexml",
            "--output-file", str(xml_path),
            "--logfile", str(destination / f"publications-{index}.blg"), str(source),
        ]
        result = subprocess.run(command, env=environment, cwd=destination, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
        diagnostics = [line for line in result.stdout.splitlines()
                       if "WARN -" in line or "ERROR -" in line]
        if result.returncode or diagnostics:
            detail = "\n".join(diagnostics or result.stdout.splitlines()[-25:])
            raise RuntimeError(f"Bibliography parsing failed for {source.name}:\n{detail}")
        for entry in ET.parse(xml_path).findall("b:entry", NS):
            if entry.get("entrytype") in {"xdata", "set"}:
                continue
            key = entry.get("id", "")
            if key in seen_keys:
                raise RuntimeError(f"Duplicate BibTeX key: {key}")
            seen_keys.add(key)
            count += 1
            def text(field: str) -> str:
                node = entry.find(f"b:{field}", NS)
                return "".join(node.itertext()).strip() if node is not None else ""
            if not text("title") or entry.find("b:names[@type='author']/b:name", NS) is None:
                raise RuntimeError(f"Publication {key!r} needs a title and at least one author.")
            if not text("date") and not text("year"):
                raise RuntimeError(f"Publication {key!r} needs a valid date or year.")
            if entry.get("entrytype") == "article" and not text("journaltitle"):
                raise RuntimeError(f"Article {key!r} needs a journaltitle.")
            if entry.get("entrytype") == "inproceedings" and not text("booktitle"):
                raise RuntimeError(f"Conference paper {key!r} needs a booktitle.")
            doi = text("doi")
            if doi:
                normalized = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", doi,
                                    flags=re.IGNORECASE).casefold()
                if not re.fullmatch(r"10\.\d{4,9}/[^\s]+", normalized):
                    raise RuntimeError(f"Invalid DOI in {key!r}: {doi}")
                if normalized in seen_dois:
                    raise RuntimeError(f"Duplicate DOI in {seen_dois[normalized]!r} and {key!r}: {doi}")
                seen_dois[normalized] = key
                if normalized != doi.casefold():
                    raise RuntimeError(f"Use the bare DOI in {key!r}, without a URL or 'doi:' prefix.")
            for field in ("url", "usera", "userb", "userc"):
                if text(field):
                    try:
                        validate_uri(normalize_uri(text(field)))
                    except ValueError as error:
                        raise RuntimeError(f"{key!r}, field {field}: {error}") from error
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bibliographies", nargs="*", type=Path)
    args = parser.parse_args()
    from build import tex_environment
    paths = args.bibliographies or sorted((ROOT / "data").rglob("*.bib"))
    try:
        with tempfile.TemporaryDirectory(prefix="academic-cv-lint-") as temporary:
            count = validate_publications([path.resolve() for path in paths],
                                          Path(temporary), tex_environment())
        print(f"Validated {count} publication records.")
    except (RuntimeError, ValueError, OSError, subprocess.TimeoutExpired, ET.ParseError) as error:
        raise SystemExit(str(error))


if __name__ == "__main__":
    main()
