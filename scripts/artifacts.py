#!/usr/bin/env python3
"""Shared source fingerprints, layout metadata, and link validation."""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "build-manifest.json"
LANGUAGES = ("en", "zh")
PDF_FILES = {"en": "cv.pdf", "zh": "cv-zh.pdf"}
MANIFEST_SCHEMA = 2
EXCLUDED = {".git", "_build", ".venv", "__pycache__", "dist"}
INPUT_SUFFIXES = {
    ".tex", ".cls", ".sty", ".bib", ".bst", ".bbx", ".cbx", ".dbx", ".def",
    ".py", ".png", ".jpg", ".jpeg", ".pdf", ".svg", ".otf", ".ttf",
}
INPUT_NAMES = {".latexmkrc", "Makefile", "requirements-build.txt", "requirements-qa.txt"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_fingerprint(root: Path = ROOT) -> dict:
    files = {}
    caches = cache_directories(root)
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in EXCLUDED for part in relative.parts) or not path.is_file():
            continue
        if any(part.startswith(".academic-cv-") for part in relative.parts):
            continue
        if any(cache == path or cache in path.parents for cache in caches):
            continue
        if path.suffix.lower() in INPUT_SUFFIXES or path.name in INPUT_NAMES:
            files[relative.as_posix()] = sha256(path)
    encoded = json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
    return {"digest": hashlib.sha256(encoded).hexdigest(), "files": files}


def cache_directories(root: Path = ROOT) -> set[Path]:
    directories = {marker.parent.resolve() for marker in root.rglob(".academic-cv-cache")}
    configured = os.environ.get("ACADEMIC_CV_BUILD_DIR")
    if configured:
        directories.add(Path(configured).expanduser().resolve())
    return directories


def normalize_uri(value: str) -> str:
    for escaped, literal in ((r"\_", "_"), (r"\%", "%"), (r"\&", "&"), (r"\#", "#")):
        value = value.replace(escaped, literal)
    return value.strip()


def validate_uri(value: str, *, email: bool = False) -> None:
    value = normalize_uri(value)
    if any(character.isspace() for character in value):
        raise ValueError(f"Link contains whitespace: {value}")
    if email:
        if not re.fullmatch(r"mailto:[^@\s]+@[^@\s]+", value):
            raise ValueError(f"Invalid email contact: {value}")
        return
    try:
        parsed = urlsplit(value)
        _ = parsed.port
    except ValueError as error:
        raise ValueError(f"Invalid link: {value}") from error
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError(f"Use a complete http(s) URL: {value}")


def validate_orcid(value: str) -> None:
    if not value:
        return
    if not re.fullmatch(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]", value):
        raise ValueError("ORCID must have the form 0000-0000-0000-0000; leave it empty if unused.")
    digits = value.replace("-", "")
    total = 0
    for digit in digits[:-1]:
        total = (total + int(digit)) * 2
    result = (12 - total % 11) % 11
    expected = "X" if result == 10 else str(result)
    if digits[-1] != expected:
        raise ValueError(f"ORCID checksum is incorrect: {value}")


def read_layout(path: Path) -> dict:
    values: dict[str, list[str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values.setdefault(key, []).append(value)
    dimensions = {}
    for key in ("page-width", "page-height", "left", "right", "body-top", "body-bottom"):
        raw = values.get(key, [""])[0]
        match = re.fullmatch(r"(-?\d+(?:\.\d+)?)pt", raw)
        if not match:
            raise ValueError(f"Missing or invalid layout dimension {key!r} in {path}")
        dimensions[key] = float(match[1]) * 72 / 72.27
    language = values.get("language", ["en-GB"])[0]
    if not re.fullmatch(r"[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*", language):
        raise ValueError(f"Invalid document language: {language}")
    contacts = sorted({normalize_uri(value) for value in values.get("contact", [])})
    resources = sorted({normalize_uri(value) for value in values.get("resource", [])})
    for uri in contacts:
        validate_uri(uri, email=uri.startswith("mailto:"))
    for uri in resources:
        validate_uri(uri)
    validate_orcid(values.get("orcid", [""])[0])
    return {
        **dimensions, "language": language, "contacts": contacts,
        "resources": resources, "sections": len(set(values.get("section", []))),
    }


def read_manifest(root: Path = ROOT) -> dict:
    path = root / "dist" / MANIFEST
    try:
        result = json.loads(path.read_text())
    except (OSError, ValueError) as error:
        raise RuntimeError("Build manifest is missing or unreadable. Run scripts/build.py.") from error
    if result.get("schema") != MANIFEST_SCHEMA:
        raise RuntimeError("Unsupported build manifest. Rebuild the CV.")
    return result


def require_current(languages=LANGUAGES, root: Path = ROOT) -> dict:
    manifest = read_manifest(root)
    current = source_fingerprint(root)["digest"]
    for language in languages:
        record = manifest.get("documents", {}).get(language)
        if not record or record.get("source_digest") != current:
            raise RuntimeError(f"{language} PDF does not match the current source. Rebuild that language.")
        pdf = root / "dist" / PDF_FILES[language]
        if not pdf.is_file() or sha256(pdf) != record.get("pdf_sha256"):
            raise RuntimeError(f"{language} PDF is missing or changed since its build. Rebuild that language.")
    return manifest
