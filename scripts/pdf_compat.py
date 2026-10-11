#!/usr/bin/env python3
"""Embed standard CJK Unicode maps so PDF viewers need no external CMaps."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile

try:
    import pypdf
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import DecodedStreamObject, NameObject
except ImportError:
    raise SystemExit("Install build dependencies: python3 -m pip install -r requirements-build.txt")

STANDARD_CJK_ORDERINGS = {"GB1", "CNS1", "Japan1", "Korea1"}


def iter_fonts(document):
    """Include fonts in form resources as well as page resources."""
    seen_resources, seen_fonts = set(), set()

    def visit(resources):
        if resources is None:
            return
        resources = resources.get_object()
        if id(resources) in seen_resources:
            return
        seen_resources.add(id(resources))
        fonts = resources.get("/Font", {})
        fonts = fonts.get_object() if hasattr(fonts, "get_object") else fonts
        for reference in fonts.values():
            font = reference.get_object()
            if id(font) not in seen_fonts:
                seen_fonts.add(id(font))
                yield font
        forms = resources.get("/XObject", {})
        forms = forms.get_object() if hasattr(forms, "get_object") else forms
        for reference in forms.values():
            form = reference.get_object()
            if form.get("/Subtype") == "/Form":
                yield from visit(form.get("/Resources"))

    for page in document.pages:
        yield from visit(page.get("/Resources"))


def missing_cjk_maps(document):
    for font in iter_fonts(document):
        if font.get("/Subtype") != "/Type0" or "/ToUnicode" in font:
            continue
        descendants = font.get("/DescendantFonts")
        if descendants is None:
            continue
        descendants = descendants.get_object()
        info = descendants[0].get_object().get("/CIDSystemInfo")
        if info is None:
            continue
        info = info.get_object()
        if info.get("/Registry") != "Adobe" or info.get("/Ordering") not in STANDARD_CJK_ORDERINGS:
            continue
        # The standard map accepts CIDs, not arbitrary font character codes.
        if font.get("/Encoding") not in {"/Identity-H", "/Identity-V"}:
            raise RuntimeError(f"Cannot attach a CID Unicode map to {font.get('/Encoding')}: "
                               f"{font.get('/BaseFont')}")
        yield font, f"Adobe-{info['/Ordering']}-UCS2"


def embed_cjk_maps(path: Path, env: dict) -> list[str]:
    """Change only missing font maps; leave glyphs and page content intact."""
    reader = PdfReader(path)
    if not list(missing_cjk_maps(reader)):
        return []
    writer = PdfWriter(clone_from=reader)
    maps = {}
    for font, name in missing_cjk_maps(writer):
        if name not in maps:
            result = subprocess.run(
                [shutil.which("kpsewhich", path=env["PATH"]), "--format=cmap", name],
                env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20,
            )
            location = result.stdout.strip()
            if result.returncode or not location or not Path(location).is_file():
                raise RuntimeError(f"Missing TeX Live character map {name}; install its CJK mapping resources.")
            # Keep the original Adobe copyright and licence inside the stream.
            stream = DecodedStreamObject()
            stream.set_data(Path(location).read_bytes())
            maps[name] = writer._add_object(stream.flate_encode())
        font[NameObject("/ToUnicode")] = maps[name]
    with tempfile.NamedTemporaryFile(prefix=".academic-cv-cmap-", suffix=".pdf",
                                     dir=path.parent, delete=False) as temporary:
        target = Path(temporary.name)
    try:
        writer.write(target)
        if list(missing_cjk_maps(PdfReader(target))):
            raise RuntimeError("CJK Unicode maps were not saved in the generated PDF.")
        os.replace(target, path)
    finally:
        target.unlink(missing_ok=True)
    return sorted(maps)


def check_unicode_text(path: Path, expected: str) -> int:
    reader = PdfReader(path)
    missing = [str(font.get("/BaseFont")) for font, _ in missing_cjk_maps(reader)]
    if missing:
        raise AssertionError(f"CJK fonts need external Unicode maps in {path.name}: {missing}")
    cjk = lambda value: {char for char in value if '\u3400' <= char <= '\u9fff'
                         or '\U00020000' <= char <= '\U000323af'}
    required = cjk(expected)
    if required:
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        lost = required - cjk(text)
        if lost:
            raise AssertionError(f"Chinese text is unreadable by a second PDF parser in {path.name}: "
                                 + "".join(sorted(lost)))
    return len(required)
