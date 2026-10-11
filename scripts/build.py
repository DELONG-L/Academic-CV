#!/usr/bin/env python3
"""Build English and Chinese CVs; publish only after the requested set succeeds."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid

from artifacts import (ROOT, MANIFEST, MANIFEST_SCHEMA, LANGUAGES, PDF_FILES,
                       read_layout, sha256, source_fingerprint)
from lint import validate_publications
from pdf_compat import embed_cjk_maps, pypdf

SOURCES = {"en": "main.tex", "zh": "cv-zh.tex"}
BAD_LOG_MESSAGES = (
    "Overfull ", "Missing character:", "undefined references",
    "undefined citations", "Please (re)run Biber", "LaTeX Error:",
)
REQUIRED_TEX_FILES = (
    "fontspec.sty", "xeCJK.sty", "xurl.sty", "bookmark.sty", "biblatex.sty",
    "texgyretermes-regular.otf", "texgyretermes-bold.otf",
    "texgyretermes-italic.otf", "texgyretermes-bolditalic.otf",
    "texgyreheros-regular.otf", "texgyreheros-bold.otf",
    "texgyreheros-italic.otf", "texgyreheros-bolditalic.otf",
    "texgyrecursor-regular.otf", "texgyrecursor-bold.otf",
    "texgyrecursor-italic.otf", "texgyrecursor-bolditalic.otf",
    "FandolSong-Regular.otf", "FandolSong-Bold.otf",
    "FandolHei-Regular.otf", "FandolHei-Bold.otf", "FandolFang-Regular.otf",
    "FandolKai-Regular.otf",
)


def build_directory() -> Path:
    path = Path(os.environ.get("ACADEMIC_CV_BUILD_DIR", ROOT / "_build")).expanduser().resolve()
    if path == ROOT or path == ROOT / "dist" or path in ROOT.parents:
        raise RuntimeError("ACADEMIC_CV_BUILD_DIR must name a dedicated build-cache directory.")
    return path


def tex_environment() -> dict[str, str]:
    env = os.environ.copy()
    tex_bin = env.get("TEXLIVE_BIN", "/Library/TeX/texbin")
    if Path(tex_bin).is_dir():
        env["PATH"] = tex_bin + os.pathsep + env.get("PATH", "")
    for executable in ("latexmk", "xelatex", "biber", "kpsewhich"):
        if shutil.which(executable, path=env.get("PATH")) is None:
            raise RuntimeError(f"{executable} was not found. Install TeX Live or set TEXLIVE_BIN.")
    return env


def check_dependencies(env: dict) -> None:
    missing = []
    for filename in REQUIRED_TEX_FILES:
        result = subprocess.run(
            [shutil.which("kpsewhich", path=env["PATH"]), filename],
            env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20,
        )
        if not result.stdout.strip():
            missing.append(filename)
    if missing:
        raise RuntimeError("Missing TeX packages or fonts: " + ", ".join(missing)
                           + ". Install the corresponding TeX Live packages.")


def compile_source(source: Path, destination: Path) -> Path:
    env = tex_environment()
    destination.mkdir(parents=True, exist_ok=True)
    command = [
        shutil.which("latexmk", path=env["PATH"]),
        "-xelatex", "-interaction=nonstopmode", "-halt-on-error",
        "-file-line-error", f"-outdir={destination}", str(source),
    ]
    result = subprocess.run(command, cwd=ROOT, env=env, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=240)
    if result.returncode:
        detail = "\n".join(result.stdout.splitlines()[-55:])
        raise RuntimeError(f"Compilation failed for {source.name}:\n{detail}")
    log_path = destination / (source.stem + ".log")
    log = log_path.read_text(errors="replace")
    problems = [line for line in log.splitlines()
                if any(message in line for message in BAD_LOG_MESSAGES)]
    if problems:
        raise RuntimeError(f"Layout or reference errors in {log_path}:\n" + "\n".join(problems))
    biber_log = destination / (source.stem + ".blg")
    if biber_log.exists():
        warnings = [line for line in biber_log.read_text(errors="replace").splitlines()
                    if "WARN -" in line or "ERROR -" in line]
        if warnings:
            raise RuntimeError("Biber diagnostics:\n" + "\n".join(warnings))
    pdf = destination / (source.stem + ".pdf")
    if not pdf.is_file():
        raise RuntimeError(f"Expected PDF is missing: {pdf}")
    read_layout(destination / (source.stem + ".cvmeta"))
    embed_cjk_maps(pdf, env)
    return pdf


def publish(staged: dict[str, Path], fingerprint: dict, versions: dict,
            root: Path = ROOT) -> None:
    """Replace the delivery directory as a set, with rollback on rename failure."""
    dist = root / "dist"
    try:
        existing = json.loads((dist / MANIFEST).read_text())
        records = existing.get("documents", {}) if existing.get("schema") == MANIFEST_SCHEMA else {}
    except (OSError, ValueError):
        records = {}
    replacement = Path(tempfile.mkdtemp(prefix=".academic-cv-stage-", dir=root))
    backup = root / (".academic-cv-backup-" + uuid.uuid4().hex)
    moved_previous = False
    try:
        # Carry forward only known language documents with matching metadata.
        # Obsolete delivery files must not survive a successful model change.
        for language in LANGUAGES:
            previous = dist / PDF_FILES[language]
            if language in records and previous.is_file():
                shutil.copy2(previous, replacement / previous.name)
            else:
                records.pop(language, None)
        for language, pdf in staged.items():
            target = replacement / PDF_FILES[language]
            shutil.copy2(pdf, target)
            records[language] = {
                "source_digest": fingerprint["digest"], "pdf_sha256": sha256(target),
                "layout": read_layout(pdf.with_suffix(".cvmeta")),
                "built_at_utc": datetime.now(timezone.utc).isoformat(), "tools": versions,
            }
        (replacement / MANIFEST).write_text(json.dumps({
            "schema": MANIFEST_SCHEMA, "sources": fingerprint["files"], "documents": records,
        }, ensure_ascii=False, indent=2) + "\n")
        if dist.exists():
            dist.rename(backup)
            moved_previous = True
        try:
            replacement.rename(dist)
        except OSError:
            if moved_previous:
                backup.rename(dist)
            raise
        if moved_previous:
            shutil.rmtree(backup)
    finally:
        if replacement.exists():
            shutil.rmtree(replacement)


def tool_versions(env: dict) -> dict:
    versions = {"pypdf": pypdf.__version__}
    for name in ("xelatex", "biber", "latexmk"):
        result = subprocess.run(
            [shutil.which(name, path=env["PATH"]), "--version"],
            env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=20,
        )
        versions[name] = next((line.strip() for line in result.stdout.splitlines()
                               if line.strip()), "unknown")
    return versions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=(*LANGUAGES, "all"), default="all")
    parser.add_argument("--clean", action="store_true", help="Remove the build cache first.")
    args = parser.parse_args()
    try:
        cache = build_directory()
        if args.clean and cache.exists():
            shutil.rmtree(cache)
        cache.mkdir(parents=True, exist_ok=True)
        (cache / ".academic-cv-cache").write_text("Generated Academic CV build cache.\n")
        env = tex_environment()
        check_dependencies(env)
        fingerprint = source_fingerprint()
        validate_publications(sorted((ROOT / "data").rglob("*.bib")), cache / "lint", env)
        languages = LANGUAGES if args.language == "all" else (args.language,)
        staged = {language: compile_source(ROOT / SOURCES[language], cache / language)
                  for language in languages}
        if source_fingerprint()["digest"] != fingerprint["digest"]:
            raise RuntimeError("Source changed during compilation. Rebuild to publish a consistent set.")
        publish(staged, fingerprint, tool_versions(env))
        for language in languages:
            print(f"Built dist/{PDF_FILES[language]}")
    except (RuntimeError, ValueError, OSError, subprocess.TimeoutExpired) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
