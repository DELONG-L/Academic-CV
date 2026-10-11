<div align="center">

<h1>Academic CV</h1>

<p>A clean LaTeX CV for research and academia.<br>English and Chinese · Serif typography · BibLaTeX publications</p>

<p>
  <a href="https://github.com/DELONG-L/Academic-CV/actions/workflows/build.yml"><img src="https://github.com/DELONG-L/Academic-CV/actions/workflows/build.yml/badge.svg?branch=main" alt="Build status"></a>
  <a href="https://github.com/DELONG-L/Academic-CV/releases/latest"><img src="https://img.shields.io/github/v/release/DELONG-L/Academic-CV?label=release&amp;color=333333" alt="Latest release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-333333" alt="MIT licence"></a>
  <a href="#get-started"><img src="https://img.shields.io/badge/engine-XeLaTeX-333333" alt="XeLaTeX compiler"></a>
</p>

<p>
  <a href="https://github.com/DELONG-L/Academic-CV/releases/latest/download/academic-cv.zip"><strong>Download source ZIP</strong></a>
  · <a href="docs/guide.md">User guide</a>
  · <a href="README.zh-CN.md">简体中文</a>
</p>

</div>

## Preview

Single column, centred name, ruled section headings, and dates aligned on the right.
Click a first-page preview to open its complete three-page PDF.

<table>
  <tr><th width="50%">English</th><th width="50%">简体中文</th></tr>
  <tr>
    <td><a href="dist/cv.pdf"><img src="docs/previews/cv-en.png" alt="First page of the English academic CV" width="420"></a></td>
    <td><a href="dist/cv-zh.pdf"><img src="docs/previews/cv-zh.png" alt="First page of the Simplified Chinese academic CV" width="420"></a></td>
  </tr>
  <tr>
    <td align="center"><a href="dist/cv.pdf">English PDF</a></td>
    <td align="center"><a href="dist/cv-zh.pdf">Chinese PDF</a></td>
  </tr>
</table>

The supplied people, institutions, publications, and achievements are fictional examples.

## Features

| Feature | What it provides |
|---|---|
| Bilingual typography | English and Simplified Chinese examples, matched font families, and CJK/Latin spacing. |
| Academic publications | BibLaTeX lists, author highlighting, J/C/P numbering, and publisher or preprint links. |
| Modular content | Separate files for education, research, teaching, service, funding, and other sections. |
| Multi-page layout | Natural page breaks, wrapping entries, PDF bookmarks, and page counts. |
| Simple styling | Serif body text, restrained rules, right-aligned dates, and optional monochrome icons. |
| Portable builds | TeX Live fonts, local and Overleaf workflows, and a ready-to-use source ZIP. |

## Get started

### Overleaf

1. [Download academic-cv.zip](https://github.com/DELONG-L/Academic-CV/releases/latest/download/academic-cv.zip).
2. In Overleaf, select **New Project → Upload Project** and upload the ZIP.
3. Set **TeX Live 2026** and the **XeLaTeX** compiler in project settings.
4. Choose `main.tex` for English or `main-zh.tex` for Chinese, then replace the example content.

The ZIP includes editable sources, both examples, PDFs, documentation, and licences.
No Git or Python installation is needed on Overleaf.

### Local

Extract the same ZIP and open a terminal in the project folder. Use an updated
**TeX Live 2026** installation, with LaTeX kernel 2026-06-01 or newer,
XeLaTeX, Biber, latexmk, and Chinese language support.

```bash
latexmk -xelatex main.tex
latexmk -xelatex main-zh.tex
```

See the [installation and build guide](docs/guide.md#quick-start) for setup,
Git cloning, and platform-specific instructions.

<details>
<summary>Build PDFs with additional CJK viewer compatibility</summary>

The Python build embeds standard CJK Unicode maps so PDF viewers can display,
search, and copy Chinese without loading external maps. It produces
`dist/cv.pdf` and `dist/cv-zh.pdf`.

With Python 3.10 or newer, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements-build.txt
python3 scripts/build.py
```

On Windows, activate the environment with `.venv\Scripts\activate` instead.

</details>

## Make it yours

| Edit | English | Chinese |
|---|---|---|
| Name and contacts | [config/profile.tex](config/profile.tex) | [config/profile-zh.tex](config/profile-zh.tex) |
| Experiences and achievements | [content/](content/) | [content/zh/](content/zh/) |
| Section order | [content/sections.tex](content/sections.tex) | [content/zh/sections.tex](content/zh/sections.tex) |
| Publications | [data/publications.bib](data/publications.bib) | [data/publications-zh.bib](data/publications-zh.bib) |

Both examples share [config/style.tex](config/style.tex) for fonts, spacing,
margins, colours, and icon settings. The class is `academic-cv.cls`, loaded with
`\documentclass{academic-cv}`.

The [user guide](docs/guide.md) covers contact links, Chinese typography,
entry layout, publication fields, author highlighting, and checks and packaging.

## Attribution and licence

MIT licensed. The modular structure and bibliography approach are inspired by
[Simple-CV](https://github.com/dcetin/Simple-CV). Academic section coverage draws on
[Academic CV by Diego](https://github.com/damascenodiego/Academic-CV-by-Diego)
and [academistral-cv](https://github.com/beyefendi/academistral-cv), without copying
their source code. See [NOTICE.md](NOTICE.md) and [licenses/](licenses/) for attribution
and third-party licence notices.
