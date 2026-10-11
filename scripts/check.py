#!/usr/bin/env python3
"""Check current PDFs against their actual geometry, contacts, and language."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import unquote

try:
    import pdfplumber
    from pdfminer.pdfdocument import PDFNoOutlines
    from pdfminer.pdftypes import resolve1
except ImportError:
    raise SystemExit("Install the optional QA dependencies: pip install -r requirements-qa.txt")

from artifacts import ROOT, LANGUAGES, PDF_FILES, normalize_uri, read_layout, require_current
from pdf_compat import check_unicode_text


def check_cjk_line_edges(page) -> None:
    # Superscript role marks sit above the baseline and can make an extractor
    # split a visual line into fragments. Check the body-size glyphs together.
    body_text = page.filter(lambda item: item.get("object_type") == "char"
                            and item.get("size", 0) > 10.5)
    for line in body_text.extract_text_lines():
        text = line["text"].strip()
        if text.startswith(tuple("，。；：！？）》】、")) or text.endswith(tuple("（《【")):
            raise AssertionError(f"Chinese punctuation broke at a line edge: {text}")


def check_link_geometry(page, layout: dict) -> None:
    links = page.hyperlinks
    for link in links:
        coordinates = [link[key] for key in ("x0", "top", "x1", "bottom")]
        if (not all(math.isfinite(value) for value in coordinates)
                or link["x1"] <= link["x0"] or link["bottom"] <= link["top"]):
            raise AssertionError(f"Invalid hyperlink rectangle: {link.get('uri')}")
        if (link["x0"] < layout["left"] - 2.5
                or link["x1"] > page.width - layout["right"] + 2.5
                or link["top"] < 0 or link["bottom"] > page.height):
            raise AssertionError(f"Hyperlink outside configured margins: {link.get('uri')}")
    for index, first in enumerate(links):
        for second in links[index + 1:]:
            if normalize_uri(first.get("uri") or "") == normalize_uri(second.get("uri") or ""):
                continue
            width = min(first["x1"], second["x1"]) - max(first["x0"], second["x0"])
            height = min(first["bottom"], second["bottom"]) - max(first["top"], second["top"])
            if width > .25 and height > .25:
                raise AssertionError("Different hyperlink targets have overlapping click areas: "
                                     f"{first.get('uri')}, {second.get('uri')}")


def inspect_pdf(path: Path, layout: dict | None = None) -> tuple[dict, str]:
    layout = layout or read_layout(path.with_suffix(".cvmeta"))
    tolerance = 2.5
    with pdfplumber.open(path) as pdf:
        texts, targets = [], set()
        links = character_count = 0
        for page_number, page in enumerate(pdf.pages, 1):
            check_link_geometry(page, layout)
            if layout["language"].startswith("zh"):
                check_cjk_line_edges(page)
            if abs(page.width - layout["page-width"]) > 1 or abs(page.height - layout["page-height"]) > 1:
                raise AssertionError(f"Page size differs from build metadata: {path.name}")
            text = page.extract_text(x_tolerance=1) or ""
            body = [char for char in page.chars if char["text"].strip()
                    and char["top"] >= layout["body-top"] - tolerance
                    and char["bottom"] <= layout["body-bottom"] + tolerance]
            if not body:
                raise AssertionError(f"Blank body: {path.name}, page {page_number}")
            if "\ufffd" in text:
                raise AssertionError(f"Replacement character in {path.name}, page {page_number}")
            for char in page.chars:
                if char["text"].isspace():
                    continue
                if char["x0"] < layout["left"] - tolerance or char["x1"] > page.width - layout["right"] + tolerance:
                    raise AssertionError(f"Text outside configured margins: {path.name}, page {page_number}, {char['text']!r}")
                if char["top"] < 5 or char["bottom"] > page.height - 5:
                    raise AssertionError(f"Text outside page: {path.name}, page {page_number}")
            text_width = page.width - layout["left"] - layout["right"]
            for rule in [*page.lines, *page.rects]:
                if rule["x1"] - rule["x0"] < text_width * .7 or abs(rule["bottom"] - rule["top"]) > 1:
                    continue
                if not any(char["top"] > rule["bottom"] for char in body):
                    raise AssertionError(f"Section heading without content: {path.name}, page {page_number}")
            footer = page.crop((0, layout["body-bottom"] + tolerance, page.width, page.height)).extract_text() or ""
            if not re.search(rf"{page_number}\s*/\s*{len(pdf.pages)}", footer):
                raise AssertionError(f"Incorrect page footer: {path.name}, page {page_number}")
            texts.append(text)
            links += len(page.hyperlinks)
            character_count += len(page.chars)
            targets.update(unquote(normalize_uri(link["uri"])) for link in page.hyperlinks if link.get("uri"))
        expected = {unquote(normalize_uri(uri)) for uri in layout["contacts"] + layout["resources"]}
        missing = expected - targets
        if missing:
            raise AssertionError(f"Expected links are missing from {path.name}: {sorted(missing)}")
        language = resolve1(pdf.doc.catalog.get("Lang", b""))
        if isinstance(language, bytes):
            language = language.decode("utf-8")
        if language != layout["language"]:
            raise AssertionError(f"Incorrect document language in {path.name}: {language!r}")
        try:
            outlines = list(pdf.doc.get_outlines())
        except PDFNoOutlines:
            outlines = []
        if len(outlines) < layout["sections"]:
            raise AssertionError(f"Section bookmarks are missing from {path.name}")
        # Resolve named destinations, rather than accepting a bookmark count
        # whose entries may point to the previous page after a forced break.
        page_ids = {page.page_obj.pageid: index for index, page in enumerate(pdf.pages)}
        compact = lambda value: re.sub(r"[\W_]+", "", value.casefold())
        for _, title, destination, action, _ in outlines:
            if destination is None and action is not None:
                destination = resolve1(action).get("D")
            if isinstance(destination, (str, bytes)):
                destination = pdf.doc.get_dest(destination)
            destination = resolve1(destination)
            if isinstance(destination, dict):
                destination = resolve1(destination.get("D"))
            if not isinstance(destination, (list, tuple)) or not destination:
                raise AssertionError(f"Invalid bookmark destination in {path.name}: {title}")
            reference = destination[0]
            index = page_ids.get(getattr(reference, "objid", None))
            if index is None or compact(title) not in compact(texts[index]):
                raise AssertionError(f"Bookmark points to a page without its heading: {path.name}, {title}")
        cjk_characters = check_unicode_text(path, "\n".join(texts))
        return {
            "file": path.name, "pages": len(pdf.pages), "characters": character_count,
            "cjk_characters_verified": cjk_characters,
            "links": links, "expected_links": len(expected), "bookmarks": len(outlines),
            "language": language, "margins_pt": {"left": round(layout["left"], 2),
                                              "right": round(layout["right"], 2)},
        }, "\n".join(texts)


def check_sample(path: Path, text: str) -> None:
    text = " ".join(text.split())
    for phrase in (
        "Funding", "Student supervision", "Invited talks", "Research software",
        "Visiting Research Student", "Education", "Research experience",
        "Teaching", "Academic service", "Journal articles", "Conference papers", "Preprints",
    ):
        if phrase.casefold() not in text.casefold():
            raise AssertionError(f"Required sample content is missing: {phrase}")
    hidden_title = "Diagnosing Evaluation Drift in Collaborative Research"
    if hidden_title in text:
        raise AssertionError("A manuscript under review leaked into the default publication list")
    if "Accepted papers".casefold() in text.casefold() or re.search(r"\[A\d+\]", text):
        raise AssertionError("A separate accepted-paper group reached the default CV")
    if re.search(r"\bin\s+press\b|\bforthcoming\b", text, re.IGNORECASE):
        raise AssertionError("A publication-state label reached the default CV")
    if text.count("Making Evaluation Reports Traceable to Research Artifacts") != 1:
        raise AssertionError("The accepted journal paper was lost or duplicated")
    for prefix, count in (("J", 4), ("C", 4), ("P", 1)):
        labels = re.findall(rf"\[{prefix}(\d+)\]", text)
        if labels != [str(i) for i in range(1, count + 1)]:
            raise AssertionError(f"Incorrect publication labels for {prefix}: {labels}")
    with pdfplumber.open(path) as pdf:
        highlighted = []
        for page in pdf.pages:
            for result in page.search(r"A\.(?:\s*Q\.)?\s*Example"):
                if not all("Bold" in char["fontname"] for char in result["chars"]
                           if char["text"].strip()):
                    raise AssertionError(f"Own author name is not bold in {path.name}")
                highlighted.append(result)
        if not highlighted:
            raise AssertionError(f"Own author name was not found in {path.name}")


def check_chinese_sample(path: Path, text: str) -> None:
    text = re.sub(r"\s+", "", text)
    with pdfplumber.open(path) as document:
        outlines = {title for _, title, _, _, _ in document.doc.get_outlines()}
    for title in ("科研项目", "学生指导", "学术报告", "研究软件"):
        if title not in outlines:
            raise AssertionError(f"Required Chinese section is missing: {title}")
    if "访问研究生" not in text:
        raise AssertionError("Chinese research entry is missing")
    for title in ("教育背景", "科研经历", "学术成果", "期刊论文", "会议论文", "教学经历"):
        if title not in text:
            raise AssertionError(f"Chinese section is missing: {title}")
    if "已接收论文" in text or re.search(r"\[A\d+\]", text):
        raise AssertionError("A separate accepted-paper group reached the Chinese CV")
    if "待刊" in text or "inpress" in text.casefold() or "forthcoming" in text.casefold():
        raise AssertionError("A publication-state label reached the Chinese CV")
    if text.count("TransparentEvaluationRecordsforCollaborativeMachineLearning") != 1:
        raise AssertionError("The accepted Chinese journal paper was lost or duplicated")
    for prefix, count in (("J", 4), ("C", 2), ("P", 1)):
        if re.findall(rf"\[{prefix}(\d+)\]", text) != [str(i) for i in range(1, count + 1)]:
            raise AssertionError(f"Incorrect Chinese publication labels for {prefix}")
    with pdfplumber.open(path) as document:
        matches = [result for page in document.pages for result in page.search("林知远")
                   if 10.5 < result["chars"][0]["size"] < 15]
        if not matches or not all("Bold" in char["fontname"] for match in matches
                                  for char in match["chars"] if char["text"].strip()):
            raise AssertionError(f"Chinese author highlighting failed: {path.name}")
    if "共同第一作者" not in text or "通讯作者" not in text:
        raise AssertionError("Chinese author legends are missing")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", action="store_true", help="Also check the supplied fictional data.")
    parser.add_argument("--language", choices=(*LANGUAGES, "all"), default="all")
    parser.add_argument("--report", type=Path, help="Write an optional JSON QA report.")
    args = parser.parse_args()
    try:
        languages = LANGUAGES if args.language == "all" else (args.language,)
        manifest = require_current(languages)
        results = []
        for language in languages:
            path = ROOT / "dist" / PDF_FILES[language]
            info, text = inspect_pdf(path, manifest["documents"][language]["layout"])
            results.append(info)
            if args.sample:
                (check_sample if language == "en" else check_chinese_sample)(path, text)
        report = {"ok": True, "sample_checks": args.sample, "documents": results}
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
    except (AssertionError, RuntimeError, ValueError, OSError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
