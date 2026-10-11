#!/usr/bin/env python3
"""Exercise real PDFs, malformed data, and failed-delivery recovery."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from unittest.mock import patch

import pdfplumber

from artifacts import ROOT, LANGUAGES, PDF_FILES, MANIFEST, require_current, sha256, source_fingerprint
from build import build_directory, compile_source, publish, tex_environment
from check import inspect_pdf, check_cjk_line_edges
from lint import validate_publications
from pdf_compat import PdfReader, PdfWriter, iter_fonts


def compile_fixture(name: str, source: str, destination: Path):
    wrapper = destination / f"{name}.tex"
    wrapper.write_text(source + "\n")
    pdf = compile_source(wrapper, destination / name)
    info, text = inspect_pdf(pdf)
    return pdf, info, " ".join(text.split())


def basic(profile: str, style: str = "", preamble: str = "") -> str:
    return (r"\documentclass{academic-cv}" + "\n" + preamble + "\n"
            + profile + "\n" + style + "\n"
            + r"\addbibresource{tests/smoke.bib}" + "\n"
            + r"\begin{document}\CVHeader\nocite{*}\CVSection{Research experience}" + "\n"
            + r"\CVEntry{Research Assistant}{2024 -- 2026}{Example University}{}{A concrete research contribution with a short description.}"
            + "\n" + r"\end{document}")


def resource_checks(destination: Path) -> None:
    source = (ROOT / "tests/resources.tex").read_text()
    environment = tex_environment()
    validate_publications([ROOT / "tests/resources.bib"], destination / "lint-resources", environment)
    icon_font_available = bool(subprocess.run(
        [shutil.which("kpsewhich", path=environment["PATH"]), "fontawesome5.sty"],
        env=environment, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=20).stdout.strip())
    fallback = r"""
\makeatletter
\let\CVOriginalIfFileExists\IfFileExists
\renewcommand{\IfFileExists}[1]{%
  \ifstrequal{#1}{fontawesome5.sty}{\@secondoftwo}{\CVOriginalIfFileExists{#1}}}
\makeatother
"""
    first_pdf = None
    for name, language, extra, icons in (
        ("resources-zh", "zh-CN", "", True),
        ("resources-en", "en-GB", "", True),
        ("resources-no-icons", "zh-CN", r"\CVStyle{icons=none}", False),
        ("resources-no-icon-font", "zh-CN", fallback, False),
    ):
        fixture = source.replace("zh-CN", language).replace(r"\begin{document}", extra + r"\begin{document}")
        pdf, info, text = compile_fixture(name, fixture, destination)
        first_pdf = first_pdf or pdf
        publisher = "出版页" if language.startswith("zh") else "Publisher"
        preprint = "预印本" if language.startswith("zh") else "Preprint"
        doi = "https://doi.org/10.1234/long_identifier_for_resource_link_layout_checks"
        url = "https://example.org/citation-url/" + "long_segment/" * 8 + "search?q=cv&tag=research%20data#methods"
        primary_labels = {
            doi: publisher, url: publisher,
            "https://arxiv.org/abs/TEMPLATE_PREPRINT": "arXiv",
            "https://arxiv.org/abs/TEMPLATE_ACCEPTED": "arXiv",
            "https://arxiv.org/abs/TEMPLATE_ACCEPTED_CONFERENCE": "arXiv",
            "https://example.org/preprints/url-only": preprint,
            "https://example.org/preprints/legacy": preprint,
        }
        if info["expected_links"] != 15 + len(primary_labels):
            raise AssertionError(f"Optional publication resources were lost or duplicated in {name}")
        if ("Accepted papers" in text or "已接收论文" in text
                or re.search(r"\[A\d+\]|\bin\s+press\b|\bforthcoming\b|待刊", text, re.IGNORECASE)):
            raise AssertionError(f"An accepted-paper group or state label reached {name}")
        for title, prefix in (
            ("Accepted Manuscript with an arXiv Version", "J"),
            ("Accepted Conference Paper with an arXiv Version", "C"),
        ):
            if text.count(title) != 1:
                raise AssertionError(f"An accepted paper was lost or duplicated: {name}, {title}")
            preceding = re.findall(r"\[([JCPUR])\d+\]", text[:text.index(title)])
            if not preceding or preceding[-1] != prefix:
                raise AssertionError(f"An accepted paper left its venue group: {name}, {title}")
        labels = (publisher, "代码", "项目") if language.startswith("zh") else (publisher, "Code", "Project")
        actual_targets, citation_targets, wrapped = [], [], []
        with pdfplumber.open(pdf) as document:
            for page in document.pages:
                visible = [char for char in page.chars if char["text"].strip()]
                for link in page.hyperlinks:
                    if "/resources/" not in link["uri"]:
                        citation_targets.append(link["uri"])
                        label = primary_labels.get(link["uri"])
                        if label is None:
                            raise AssertionError(f"An unused publication URL was printed: {name}, {link['uri']}")
                    else:
                        actual_targets.append(link["uri"])
                        suffix = link["uri"].split("?")[0].rsplit("/", 1)[-1]
                        label = labels[("article", "code", "project").index(suffix)]
                    chars = [char for char in visible
                             if link["x0"] - .1 <= (char["x0"] + char["x1"]) / 2 <= link["x1"] + .1
                             and link["top"] - 2.5 <= (char["top"] + char["bottom"]) / 2 <= link["bottom"] + 2.5]
                    text = "".join(char["text"] for char in chars if "FontAwesome" not in char["fontname"])
                    icon_count = sum("FontAwesome" in char["fontname"] for char in chars)
                    if text != label or icon_count != int(icons and icon_font_available):
                        raise AssertionError(f"A resource label or its icon split outside its link: {name}, {link['uri']}")
                    if "/wrap/" in link["uri"]:
                        wrapped.append(link)
                for dot in [char for char in visible if char["text"] == "•"]:
                    middle = (dot["top"] + dot["bottom"]) / 2
                    row = [char for char in visible
                           if abs((char["top"] + char["bottom"]) / 2 - middle) < 4]
                    left = [char for char in row if char["x1"] <= dot["x0"] + .1]
                    right = [char for char in row if char["x0"] >= dot["x1"] - .1]
                    if not left or not right:
                        raise AssertionError(f"An orphan resource separator reached a line edge: {name}")
                    previous, following = max(left, key=lambda char: char["x1"]), min(right, key=lambda char: char["x0"])
                    if (dot["x0"] - previous["x1"] < 3 or following["x0"] - dot["x1"] < 3
                            or previous["text"] == "•" or following["text"] == "•"):
                        raise AssertionError(f"Resource separators overlap neighboring glyphs: {name}")
                    if not any(abs(link["x0"] - following["x0"]) < 1
                               and link["top"] - 2.5 < middle < link["bottom"] + 2.5
                               for link in page.hyperlinks):
                        raise AssertionError(f"A trailing separator has no resource link: {name}")
        special = "https://example.org/resources/all/code?file=src_main.py&tag=cv%20test#usage"
        if len(actual_targets) != 15 or special not in actual_targets:
            raise AssertionError(f"URL query parameters, percent encoding, or fragments changed in {name}")
        if set(citation_targets) != set(primary_labels) or len(citation_targets) != len(primary_labels):
            raise AssertionError(f"Publication status routing lost or duplicated a primary link: {name}")
        if len(wrapped) != 3 or wrapped[-1]["top"] <= wrapped[0]["top"] + 4:
            raise AssertionError(f"The resource row did not wrap between whole links: {name}")

    # Real annotation corruption must be caught even when visible text is fine.
    from pypdf.generic import ArrayObject, FloatObject, NameObject
    for name, expected in (("overlap", "overlapping click areas"), ("outside", "outside configured margins")):
        writer = PdfWriter(clone_from=PdfReader(first_pdf))
        annotations = writer.pages[0]["/Annots"]
        links = [item.get_object() for item in annotations if item.get_object().get("/Subtype") == "/Link"]
        if name == "overlap":
            links[1][NameObject("/Rect")] = ArrayObject(links[0]["/Rect"])
        else:
            links[0]["/Rect"][0] = FloatObject(0)
        broken = destination / f"invalid-link-{name}.pdf"
        writer.write(broken)
        shutil.copy2(first_pdf.with_suffix(".cvmeta"), broken.with_suffix(".cvmeta"))
        try:
            inspect_pdf(broken)
        except AssertionError as error:
            if expected not in str(error):
                raise
        else:
            raise AssertionError(f"PDF checks accepted invalid link geometry: {name}")
    print("Resource checks passed: publication status and DOI/arXiv/URL routing, all field subsets, CJK/English, icon fallback, separator spacing, whole-link wrapping, exact targets, and annotation geometry.")


def delivery_checks(destination: Path, fixtures: dict) -> None:
    # A rename failure after moving the previous delivery must restore it.
    target = destination / "publish-recovery"
    if target.exists():
        shutil.rmtree(target)
    (target / "dist").mkdir(parents=True)
    shutil.copy2(fixtures["en"], target / "dist/obsolete.pdf")
    (target / "dist" / MANIFEST).write_text(json.dumps({"schema": 1}))
    staged = {language: fixtures[language] for language in LANGUAGES}
    publish(staged, source_fingerprint(target), {"fixture": "test"}, root=target)
    if {path.name for path in (target / "dist").iterdir()} != {*PDF_FILES.values(), MANIFEST}:
        raise AssertionError("A successful build retained obsolete delivery files")
    require_current(root=target)
    previous_chinese = sha256(target / "dist" / PDF_FILES["zh"])
    publish({"en": fixtures["en"]}, source_fingerprint(target), {"fixture": "partial"}, root=target)
    require_current(root=target)
    if sha256(target / "dist" / PDF_FILES["zh"]) != previous_chinese:
        raise AssertionError("A single-language build replaced the other language PDF")
    before = {path.name: sha256(path) for path in (target / "dist").iterdir() if path.is_file()}
    original_rename = Path.rename
    def fail_commit(path, renamed):
        if path.name.startswith(".academic-cv-stage-"):
            raise OSError("Injected delivery rename failure")
        return original_rename(path, renamed)
    with patch.object(Path, "rename", fail_commit):
        try:
            publish(staged, source_fingerprint(target), {}, root=target)
        except OSError as error:
            if "Injected" not in str(error):
                raise
        else:
            raise AssertionError("Injected delivery failure did not fail")
    after = {path.name: sha256(path) for path in (target / "dist").iterdir() if path.is_file()}
    if before != after:
        raise AssertionError("Failed delivery changed the previous files")

    # English compilation succeeds, Chinese compilation fails, and neither
    # delivered PDF may be replaced.
    require_current()
    clone = destination / "failed-build-project"
    if clone.exists():
        shutil.rmtree(clone)
    shutil.copytree(ROOT, clone, ignore=shutil.ignore_patterns(
        "_build", "__pycache__", ".git", ".venv", ".academic-cv-*"))
    before = {name: sha256(clone / "dist" / name)
              for name in (*PDF_FILES.values(), MANIFEST)}
    chinese = clone / "cv-zh.tex"
    chinese.write_text(chinese.read_text().replace(r"\begin{document}",
                        r"\begin{document}\UndefinedCVRegressionCommand"))
    env = os.environ.copy()
    env["ACADEMIC_CV_BUILD_DIR"] = str(clone / "_build")
    result = subprocess.run([sys.executable, "scripts/build.py"], cwd=clone, env=env,
                            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
    if result.returncode == 0 or "Compilation failed for cv-zh.tex" not in result.stdout:
        raise AssertionError("The intended Chinese compilation failure was not observed:\n"
                             + result.stdout[-2500:])
    after = {name: sha256(clone / "dist" / name) for name in before}
    if before != after:
        raise AssertionError("A partial build replaced the delivered PDFs or manifest")
    archive = destination / "stale-source.zip"
    result = subprocess.run([sys.executable, "scripts/pack.py", "--output", str(archive)],
                            cwd=clone, env=env, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
    if result.returncode == 0 or archive.exists() or "current source" not in result.stdout:
        raise AssertionError("Packaging accepted stale PDFs")
    print("Delivery checks passed: obsolete files are removed; single-language builds preserve the other PDF; failed builds and renames preserve both PDFs; stale packages are rejected.")


def main() -> None:
    destination = build_directory() / "smoke"
    destination.mkdir(parents=True, exist_ok=True)
    resource_checks(destination)
    section_source = (ROOT / "tests/section-break.tex").read_text()
    for name, extra in (("section-break-en", ""), ("section-break-zh", r"\CVSetup{language={zh-CN}}")):
        source = section_source.replace(r"\begin{document}", extra + r"\begin{document}")
        if extra:
            source = source.replace("Supervision and collaborative research: reproducible evaluation, scientific workflows, and responsible data practice",
                                    "学生指导与协作科研：可复现实验、科学工作流、数据溯源、评估一致性与研究软件的长期维护")
        pdf, info, _ = compile_fixture(name, source, destination)
        with pdfplumber.open(pdf) as document:
            text = (document.pages[1].extract_text() or "").casefold() if len(document.pages) > 1 else ""
            if (info["pages"] != 2 or "boundary" not in text
                    or ("学生指导" if extra else "supervision") not in text
                    or "description" not in text):
                raise AssertionError(f"A wrapped section heading separated from its first entry: {name}")
    # Editorial page breaks are deferred: disabling a section must not move
    # later content or leave a blank final page. Inspect real bookmark targets
    # through compile_fixture/inspect_pdf as well as the rendered page text.
    empty_section = destination / "empty-section.tex"
    empty_section.write_text("% Intentionally empty section fixture.\n")
    full_section = destination / "full-section.tex"
    full_section.write_text(r"\CVParagraph{Editorial break content.}" + "\n")
    for language in LANGUAGES:
        source = (r"\documentclass{academic-cv}" + "\n"
                  + rf"\CVSetup{{name={{Page Test}},language={{{'zh-CN' if language == 'zh' else 'en-GB'}}}}}"
                  + r"\begin{document}\CVHeader\CVSection{First section}"
                  + r"\CVParagraph{Content before the empty section.}"
                  + rf"\CVIncludeSection*{{Hidden section}}{{{empty_section.as_posix()}}}"
                  + r"\CVSection{Continued section}\CVParagraph{Content after the empty section.}"
                  + rf"\CVIncludeSection*{{New page section}}{{{full_section.as_posix()}}}"
                  + rf"\CVIncludeSection*{{Hidden final section}}{{{empty_section.as_posix()}}}"
                  + r"\end{document}")
        pdf, info, _ = compile_fixture("editorial-break-" + language, source, destination)
        with pdfplumber.open(pdf) as document:
            texts = [re.sub(r"\s+", "", page.extract_text() or "").casefold()
                     for page in document.pages]
            first, second = texts[0], texts[1] if len(texts) > 1 else ""
            if (info["pages"] != 2 or "aftertheemptysection" not in first
                    or "newpagesection" not in second or "editorialbreakcontent" not in second
                    or "hidden" in first + second):
                raise AssertionError(f"Deferred editorial page breaks failed: {language}")
    fixtures = {}
    source = (ROOT / "tests/smoke.tex").read_text()
    for language in LANGUAGES:
        fixture = source
        if language == "zh":
            fixture = fixture.replace(r"\begin{document}",
                r"\CVSetup{language={zh-CN}}\begin{document}")
        pdf, _, text = compile_fixture("smoke-" + language,
            r"\documentclass{academic-cv}" + "\n" + fixture, destination)
        fixtures[language] = pdf
        if "示例研究者" not in text:
            raise AssertionError("Chinese characters were lost from the text layer")
        with pdfplumber.open(pdf) as document:
            matches = [match for page in document.pages for match in page.search(r"A\.\s*Example")]
            if not matches or not all("Bold" in char["fontname"]
                for match in matches for char in match["chars"] if char["text"].strip()):
                raise AssertionError("Author highlighting failed")
        cofirst, corresponding = (("Equal contribution.", "Corresponding author.")
            if language == "en" else ("共同第一作者", "通讯作者"))
        if cofirst not in text:
            raise AssertionError("Co-first-author legend is missing")
        if corresponding not in text:
            raise AssertionError("Corresponding-author legend is missing")
        if "Empty fixture section".casefold() in text.casefold():
            raise AssertionError("An empty section was printed")
        for phrase in ("Research assistant", "Visiting researcher", "Service item", "[J1]", "[P1]"):
            if phrase not in text:
                raise AssertionError(f"Fixture content is missing from {language}: {phrase}")

    # Reproduce the export that goes blank in viewers without external CMaps.
    unmapped = destination / "unmapped-cjk.pdf"
    writer = PdfWriter(clone_from=PdfReader(fixtures["en"]))
    removed = 0
    for font in iter_fonts(writer):
        if "Fandol" in str(font.get("/BaseFont", "")) and "/ToUnicode" in font:
            del font["/ToUnicode"]
            removed += 1
    if not removed:
        raise AssertionError("The CJK viewer regression fixture had no embedded maps")
    writer.write(unmapped)
    shutil.copy2(fixtures["en"].with_suffix(".cvmeta"), unmapped.with_suffix(".cvmeta"))
    try:
        inspect_pdf(unmapped)
    except AssertionError as error:
        if "need external Unicode maps" not in str(error):
            raise
    else:
        raise AssertionError("PDF checks accepted CJK fonts without Unicode maps")

    profile = (r"\CVSetup{name={Alex Example},email={alex_research@example.edu},"
               r"github={https://example.org/alex-example/github},github-label={GitHub},"
               r"linkedin={https://example.org/alex-example/linkedin},updated={October 2026}}")
    _, info, _ = compile_fixture("no-contact", basic(
        r"\CVSetup{name={Alex Example},updated={October 2026}}"), destination)
    if info["links"]:
        raise AssertionError("No-contact fixture unexpectedly has links")
    compile_fixture("narrow-margins", basic(profile,
        r"\CVStyle{margins={left=15mm,right=15mm,top=18mm,bottom=21mm}}"), destination)
    # This checksum-valid identifier is a formatting fixture, not a claim
    # that an ORCID is registered to the example person.
    _, _, contact_text = compile_fixture("academic-contacts", basic(
        r"\CVSetup{name={Contact format fixture},email={test_contact@example.edu},"
        r"scholar={https://example.org/scholar},orcid={0000-0000-0000-0001},"
        r"github={https://example.org/alex_research/github},github-label={GitHub},"
        r"linkedin={https://example.org/alex_research/linkedin?from=cv\&lang=en\#about},"
        r"linkedin-label={领英},"
        r"phone={+00 1234 5678},location={Example City},language={zh-CN}}"), destination)
    if "GitHub" not in contact_text or "领英" not in contact_text:
        raise AssertionError("Custom social-profile labels did not appear in the header")
    long_url = "https://example.org/" + "long_segment/" * 16 + "search?q=cv&tag=research#methods"
    _, _, text = compile_fixture("long-url", basic(
        r"\CVSetup{name={Alex Example},email={alex_research@example.edu},website={"
        + long_url.replace("&", r"\&").replace("#", r"\#")
        + r"},github={https://example.org/" + "long_segment/" * 12
        + r"},updated={October 2026}}"), destination)
    if "example.org" not in text or "alex_research@example.edu" not in text:
        raise AssertionError("Automatic URL labels or underscore emails failed")
    for name, style, preamble in (
        ("icons-none", r"\CVStyle{icons=none}", ""),
        ("icons-unavailable", "", r"""
\makeatletter
\let\CVOriginalIfFileExists\IfFileExists
\renewcommand{\IfFileExists}[1]{%
  \ifstrequal{#1}{fontawesome5.sty}{\@secondoftwo}{\CVOriginalIfFileExists{#1}}}
\makeatother
"""),
        ("stacked", r"\CVStyle{entry-layout=stacked,density=compact}", ""),
    ):
        pdf, _, _ = compile_fixture(name, basic(profile, style, preamble), destination)
        if name.startswith("icons-"):
            with pdfplumber.open(pdf) as document:
                if any("FontAwesome" in char["fontname"] for page in document.pages for char in page.chars):
                    raise AssertionError(f"Icon-free fallback failed for {name}")
                text = " ".join(page.extract_text() or "" for page in document.pages)
                if "GitHub" not in text or "LinkedIn" not in text:
                    raise AssertionError(f"Social-profile labels disappeared without icons in {name}")
    _, _, full_names = compile_fixture("author-options",
        r"\documentclass{academic-cv}\CVStyle{max-authors=1,author-names=full}" + "\n"
        + r"\input{tests/smoke.tex}", destination)
    if "Alex Example" not in full_names or "et al." not in full_names:
        raise AssertionError("Author-name and truncation options failed")

    chinese = (r"\documentclass{academic-cv}\input{config/style.tex}"
        r"\input{config/profile-zh.tex}\addbibresource{data/publications-zh.bib}"
        r"\begin{document}\CVHeader\CVSection{科研经历}"
        r"\CVEntry{可信机器学习与科学软件评估：数据溯源、协作实验记录与可复现研究流程}"
        r"{2023年9月 -- 2026年10月}{示范大学跨学科科学计算与可信评估联合研究中心}{示范市}"
        r"{讨论数据质量（完整性、一致性与来源）、模型评估和 Python 工具；保留原始论文署名。}"
        r"\CVSection{学术成果}\nocite{*}"
        r"\CVPublicationGroup{conference}{会议论文}{C}\CVAuthorLegend\end{document}")
    for name, extra in (("chinese-layout", ""),
                        ("chinese-truncated", r"\CVStyle{max-authors=1,line-spread=1.16,icons=none}")):
        source = chinese.replace(r"\begin{document}", extra + r"\begin{document}")
        pdf, info, text = compile_fixture(name, source, destination)
        if info["language"] != "zh-CN" or "林知远" not in text or "共同第一作者" not in text:
            raise AssertionError(f"Chinese names, language, or legends failed: {name}")
        if name == "chinese-truncated" and "等" not in text:
            raise AssertionError("Chinese author truncation lost its marker")
        with pdfplumber.open(pdf) as document:
            names = [match for page in document.pages for match in page.search("林知远")
                     if 10.5 < match["chars"][0]["size"] < 15]
            if not names or not all("Bold" in char["fontname"] for match in names for char in match["chars"]):
                raise AssertionError("Chinese author names are not entirely bold")
            for page in document.pages:
                check_cjk_line_edges(page)

    typography = (ROOT / "tests/typography-zh.tex").read_text()
    for name, extra, family in (
        ("chinese-typography", "", "FandolSong-Bold"),
        ("chinese-typography-sans",
         r"\CVStyle{cjk-entry-family=sans,cjk-latin-gap=.28em,line-spread=1.12}",
         "FandolHei-Bold"),
    ):
        source = typography.replace(r"\begin{document}", extra + r"\begin{document}")
        pdf, _, _ = compile_fixture(name, source, destination)
        widths = {key: float(value) for key, value in re.findall(
            r"CV(implicit|explicit|boldimplicit|boldexplicit)=([\d.]+)pt",
            pdf.with_suffix(".log").read_text())}
        for prefix in ("", "bold"):
            if abs(widths[prefix + "implicit"] - widths[prefix + "explicit"]) > .02:
                raise AssertionError(f"Manual spaces changed CJK/Latin spacing in {name}")
        with pdfplumber.open(pdf) as document:
            page = document.pages[0]
            heading = page.search("可信机器学习评估")[0]
            if not all(family in char["fontname"] for char in heading["chars"]):
                raise AssertionError(f"Chinese entry font selection failed in {name}")
            date = page.search("2023")[0]
            if abs(heading["chars"][0]["matrix"][5] - date["chars"][0]["matrix"][5]) > 1.5:
                raise AssertionError(f"Entry title and date baselines differ in {name}")
            sections = [match for match in page.search(r"AI\s*与可信计算")
                        if 11.5 < match["chars"][0]["size"] < 15]
            if not sections or not any("TeXGyreHeros" in char["fontname"]
                                       for char in sections[0]["chars"]):
                raise AssertionError(f"Mixed-language section heading lost its sans serif font in {name}")

    for case, keywords in (("missing", ""), ("conflicting", "journal,preprint"),
                           ("legacy-accepted", "accepted")):
        case_directory = destination / case
        if case_directory.exists():
            shutil.rmtree(case_directory)
        bibliography = destination / f"invalid-{case}.bib"
        bibliography.write_text("@article{invalid-record, author={Example, Alex}, title={Invalid status fixture},\n"
                                + "journaltitle={Example Journal}, date={2026}, keywords={" + keywords + "}}\n")
        wrapper = destination / f"invalid-{case}.tex"
        wrapper.write_text(r"\documentclass{academic-cv}" + "\n"
            + rf"\addbibresource{{{bibliography.as_posix()}}}" + "\n"
            + r"\begin{document}\nocite{*}\CVSection{Publications}" + "\n"
            + r"\CVPublicationGroup{journal}{Journal articles}{J}\end{document}" + "\n")
        try:
            compile_source(wrapper, case_directory)
        except RuntimeError as error:
            if "group keyword" not in str(error):
                raise
        else:
            raise AssertionError(f"Invalid publication status was accepted: {case}")

    for case, data, expected in (
        ("duplicate-doi",
         "@article{one,author={Example,Alex},title={One},journaltitle={Example},date={2026},doi={10.1234/fixture}}\n"
         "@article{two,author={Example,Alex},title={Two},journaltitle={Example},date={2026},doi={10.1234/FIXTURE}}", "Duplicate DOI"),
        ("missing-title", "@article{one,author={Example,Alex},journaltitle={Example},date={2026}}", "title"),
        ("invalid-date", "@article{one,author={Example,Alex},title={One},journaltitle={Example},date={2026-13-99}}", "date"),
        ("invalid-link", "@article{one,author={Example,Alex},title={One},journaltitle={Example},date={2026},userb={not-a-url}}", "URL"),
    ):
        source = destination / f"{case}.bib"
        source.write_text(data + "\n")
        try:
            validate_publications([source], destination / ("lint-" + case), tex_environment())
        except RuntimeError as error:
            if expected.casefold() not in str(error).casefold():
                raise
        else:
            raise AssertionError(f"Invalid publication metadata was accepted: {case}")
    try:
        compile_fixture("invalid-orcid", basic(profile + r"\CVSetup{orcid={0000-0002-1825-0098}}"), destination)
    except ValueError as error:
        if "checksum" not in str(error):
            raise
    else:
        raise AssertionError("Invalid ORCID was accepted")
    print("PDF checks passed: CJK typography and spacing, special-character contacts, long URLs, optional contacts, actual margins, icons/fallback, layouts, author marks, and explicit statuses.")
    delivery_checks(destination, fixtures)


if __name__ == "__main__":
    main()
