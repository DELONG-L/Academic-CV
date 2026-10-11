# Academic CV

A maintainable LaTeX academic CV with a single column, serif typography,
centred name, ruled section headings, and dates aligned on the right.

The class file is `academic-cv.cls`; load it with `\documentclass{academic-cv}`.

[简体中文](README.zh-CN.md) · [English example](dist/cv.pdf) · [Chinese example](dist/cv-zh.pdf)

The people, institutions, publications, and achievements in the supplied
example are fictional. They are not the project owner's personal information.

## Preview

Click either first-page preview to open the complete three-page PDF.

<table>
  <tr><th>English</th><th>简体中文</th></tr>
  <tr>
    <td><a href="dist/cv.pdf"><img src="docs/previews/cv-en.png" alt="First page of the English academic CV" width="420"></a></td>
    <td><a href="dist/cv-zh.pdf"><img src="docs/previews/cv-zh.png" alt="First page of the Simplified Chinese academic CV" width="420"></a></td>
  </tr>
</table>

## Features

- Single-column serif layout, restrained section rules, and right-aligned dates.
- English and Simplified Chinese examples, with matched fonts and CJK/Latin spacing.
- Modular sections for education, research, teaching, service, funding, and other academic activities.
- BibLaTeX publication lists, author highlighting, and publisher or preprint links.
- Small monochrome contact and resource icons, with a text-only fallback.
- Automatic wrapping and pagination, PDF bookmarks, and page counts.
- Local and Overleaf builds, with automated data, PDF, and layout checks.

## Quick start

Use Python 3.10 or newer. Install TeX Live with XeLaTeX, Biber, latexmk, and Chinese language support,
to build both examples.

For Ubuntu 24.04, install the TeX dependencies with:

```bash
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  texlive-xetex texlive-latex-extra texlive-fonts-recommended \
  texlive-fonts-extra texlive-lang-chinese texlive-bibtex-extra \
  fonts-texgyre biber latexmk python3-venv
```

Then clone the repository and build:

```bash
git clone https://github.com/DELONG-L/Academic-CV.git
cd Academic-CV
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements-build.txt
python3 scripts/build.py
```

On Windows, activate the environment with `.venv\Scripts\activate` instead.

The default build produces an English CV (`dist/cv.pdf`) and a Simplified
Chinese CV (`dist/cv-zh.pdf`). Build caches
are stored in `_build/`, or in `ACADEMIC_CV_BUILD_DIR` when set. On macOS the script automatically finds
`/Library/TeX/texbin`; elsewhere use PATH or the `TEXLIVE_BIN` environment variable.

The build uses `pypdf` to embed missing CJK Unicode maps. Viewers can display,
search, and copy Chinese without downloading external Adobe CMaps. This step
preserves fonts, page content, and pagination; text remains vector text.

All language documents requested by a single build must succeed before any delivered PDF
is replaced. `dist/build-manifest.json` records source fingerprints, PDF checksums,
actual layout, contacts, and tool versions for checking and packaging. It is
maintenance data, not visible CV content. A failed build preserves the previous
delivery; checks and packaging detect whether it is stale.

To build one language locally, use `scripts/build.py --language en` or `zh`.

## Use on Overleaf

1. Download the repository using **Code → Download ZIP**, or generate a ZIP with `python3 scripts/pack.py` after building both examples.
2. In Overleaf, choose **New Project → Upload Project** and upload the ZIP.
3. Set the compiler to **XeLaTeX**.
4. Select `main.tex` for English or `cv-zh.tex` for Simplified Chinese as the main document.

Overleaf supports the template's BibLaTeX/Biber workflow.

Direct TeX and Overleaf compilation do not run the Python map-embedding step.
If an embedded viewer omits Chinese while macOS Preview displays it correctly,
use `scripts/build.py` to generate the compatible delivery PDFs.

## Edit

- `config/profile.tex`: name, position, affiliation, contact fields, update month, and author name.
- `config/style.tex`: fonts, accent colour, margins, and date column width.
- `content/sections.tex`: section order and enabled sections.
- `content/*.tex`: education, research, teaching, service, and other entries.
- `data/publications.bib`: publication metadata and status.
- `config/profile-zh.tex`, `content/zh/`, `data/publications-zh.bib`: independent Chinese example data.

The position and affiliation share one line below the name, separated by a dot.
Header rows share a consistent gap.
Leaving either field empty removes the separator; longer text wraps naturally.

Empty contact fields disappear with their separators. TeX Gyre fonts and
Fandol Chinese fonts are included in TeX Live; no external font download is needed.

Contact values accept a bare underscore. In TeX source, write `\%`, `\&`,
and `\#` for escaped URI characters; ordinary prose fields still follow
LaTeX escaping rules. An omitted website label displays the domain while
retaining the full target URL. Website, GitHub, and LinkedIn links appear in
the contact row below the name. GitHub's default label omits the protocol and
allows line breaks; LinkedIn's default label is `LinkedIn`.
`scholar` and `scholar-label` add an academic profile link.
ORCID format and checksum are validated without assuming whose ID it is.
`language={en-GB}` or `language={zh-CN}` sets the PDF language. Chinese
also enables localized typography and resource labels; it does not translate
content. `footer-name` provides an optional short footer name.

Add social profile links in `config/profile.tex` or `config/profile-zh.tex`:

```latex
\CVSetup{
  github={https://example.org/your-profile/github},
  github-label={GitHub},
  linkedin={https://example.org/your-profile/linkedin},
  linkedin-label={LinkedIn}
}
```

The examples use the reserved domain `example.org`; replace these targets
with your own profile URLs. To show only one platform, leave the other URL
empty; its icon, label, and separator disappear automatically.

## Chinese typography

The Simplified Chinese preset uses TeX Live's Fandol Song for body text,
bold Song for entry titles and publication groups, bold Fandol Hei for
the name, and regular Fandol Hei for section headings. Institutional names stay upright.
Body text remains 11 pt, sections are 12 pt, and the name is 22 pt,
with a default line-spread multiplier of `1.15`.
Latin text uses TeX Gyre Heros in the name and sections, and TeX Gyre Termes
in the body and entries, matching their Chinese font families.
The Chinese example uses a `46mm` date column to keep year/month ranges together.
It does not depend on system-specific macOS or Windows fonts.

CJK/Latin boundaries use a consistent `0.20em` gap, including manually typed
spaces and bold inline text. Compact Chinese punctuation keeps sentence-ending
marks full width and disables hanging at margins. Original English publication
punctuation and italics remain unchanged. Set `cjk-latin-gap` to a non-negative
length, or `cjk-entry-family=sans` for bold sans serif entry headings;
the default entry family is `serif`.

Set `language={zh-CN}` in the profile. This localizes PDF titles, author-role
legends, and resource labels. Maintain Chinese prose in `content/zh/`;
retain original publication titles and author spellings. There is no automatic
translation or Simplified/Traditional conversion.

`line-spread` adjusts leading. `cjk-font` and `cjk-sans-font` can select installed
CJK body and heading font families. Verify their bold weights, punctuation,
character coverage, and pagination after changing fonts. The supplied preset
and tests cover Simplified Chinese; Traditional Chinese and rare characters
need fonts covering the required characters and a review of the rendered PDF.

Store Chinese author names as family and given names, and annotate them explicitly:

```bibtex
author    = {林, 知远 and 周, 亦宁},
author+an = {1=cjk,highlight,cofirst; 2=cjk,cofirst},
```

The result keeps the complete names, family first, with role marks after each
complete name. Romanized names retain the ordinary English format. Truncated
CJK name lists end with 等. Add `chinese` to a Chinese publication's `keywords`
to use upright venue names and omit English `In:` and page prefixes; this
does not change its publication status. The CV uses BibLaTeX's numeric style
and does not claim GB/T 7714 conformance.

## Icons and layout

```latex
\CVStyle{icons=minimal,density=compact,entry-layout=auto}
```

- `icons=minimal` adds small monochrome icons to contacts and paper resources;
  `icons=none` uses plain text. Labels remain visible in both modes.
- `density=classic` uses default spacing; `compact` reduces spacing while
  retaining the 11 pt font. All supplied examples use compact spacing.
  Both presets separate sections more generously than individual entries.
  Publication group headings stay close to their first citation.
- `entry-layout=auto` measures the heading and switches a tall heading to
  a stacked layout. `columns` and `stacked` force either layout.
- `stack-threshold` defaults to `3.5\baselineskip`; `date-width` defaults to `33mm`.
- `max-authors` defaults to `99`. `author-names=initials|full` controls given names.
- `line-spread` defaults to `1` in English and `1.15` in Chinese; it can be overridden.

Font Awesome 5 is an optional TeX-distribution dependency. Academic profile
links use a generic academic icon from the same set; a missing package falls back to text.
When `accsupp` is available, decorative icons receive empty copy text.
Bookmarks and document-language metadata do not constitute PDF/UA certification.

```latex
\CVEntry{Research Assistant}{2024 -- 2026}
  {University / Research Group}{City, Country}{
  \begin{cvitems}
    \item Describe a concrete contribution.
  \end{cvitems}
}
```

The five fields are title, date, institution or role, location or short extra
information, and description. Use `\CVLine{Title}{Date}{Details}` for shorter
entries and `\CVParagraph{Text}` for ordinary paragraphs. All entries appear
in the corresponding language's CV.

Dates, locations, and short role labels use the same 10 pt upright dark gray
style in both languages and in column or stacked layouts.

Reorder or comment out lines in `content/sections.tex` or
`content/zh/sections.tex` to arrange or disable sections.
`\CVIncludeSection{Title}{File}` reads a section file. Keep section text inside
the entry or paragraph commands so empty section headings can be omitted.

Both language examples use natural page breaks, allowing publications to
follow the preceding content. Use `\CVIncludeSection*{Title}{File}` when a
section needs to start on a new page. The break occurs only when the section
prints content, so empty sections do not leave a page break. Page bottoms
remain natural, without stretching paragraphs to fill the page.

Page count follows the content. Shorten the CV by removing entries or editing
prose in the section files.

## Publications

Set exactly one group keyword per record: `journal`, `conference`,
`preprint`, or `underreview`. The template sorts entries by descending year.
The default groups use J, C, and P prefixes.

Published and accepted papers share their journal or conference group and
numbering. There is no separate accepted-paper group or printed pending-publication
label. For an accepted paper awaiting formal publication, retain
`pubstate={inpress}` or `pubstate={forthcoming}` in the source data so the template
can choose its public preprint link:

```bibtex
keywords = {journal}, % Use conference for a conference paper.
pubstate = {inpress},
```

Choose preprints for inclusion based on their contribution, relevance, and impact;
keep the records you want to display in the bibliography data.
The under-review group is disabled by default and can be enabled separately
in `content/publications.tex`. Group and publication state are supplied explicitly,
never inferred from dates, entry types, or missing links.
The template rejects missing or conflicting group keywords and reports the
affected BibTeX key.

`\CVAuthorName{Given}{Family}` highlights the exact full name stored in the
bibliography. For a name variant, use the BibLaTeX name annotation
`author+an={1=highlight}` to mark author 1 explicitly. Group numbers can
change when content changes; use BibTeX keys or DOIs for stable identification.

`author+an={1=highlight,cofirst; 2=cofirst; 3=corresponding}` marks
explicit author positions. `cofirst` displays † and `corresponding` displays *.
`\CVAuthorLegend` explains only marks actually printed in the document.
Supply roles from the paper itself. Author truncation can omit the CV owner;
review the output when reducing `max-authors`.

Each paper has at most one primary link. Published `journal` and `conference`
entries display `Publisher`, using the DOI first, then a publisher landing
page in `url`, then the legacy `usera` field. Use the bare DOI in `doi`.
Remove `inpress` or `forthcoming` once the paper is formally published.

Before formal publication (journal/conference papers with `pubstate={inpress}`
or `pubstate={forthcoming}`, plus `preprint` and `underreview` records),
`eprinttype={arxiv}` and a real bare ID in `eprint` display an `arXiv` link
to the abstract page. Otherwise, `url` or the legacy `usera` field displays
`Preprint`. Supply a public repository landing page rather than a PDF
download URL; leave the link absent when no public page exists.
The identifiers remain in the bibliography data, but full identifiers
and long URLs are hidden by default to avoid duplicate links.
Fictional examples use reserved `example.org` pages rather than real papers.

Optional `userb` and `userc` fields add `Code` and `Project` links.
Resource labels use 10 pt dark gray text and smaller icons, keeping them
visually subordinate to the 11 pt citation text. Section rules are 0.3 pt
and use a lighter tint of the configured accent color.

Bibliographies align to the left so long titles and short link labels can
wrap within the margins. Each resource icon stays with its label, while
the row can wrap between links.
Separators disappear at line breaks; empty fields do not add extra dots.
Contacts and bibliographies keep a minimum baseline distance of `1.45em`
to avoid overlapping click areas after wrapping. Larger spacing is preserved;
the body's `line-spread` setting is unchanged.
Keep `academic-cv.dbx` beside the class: it declares these fields as URLs so
Biber preserves special characters. Enter raw URLs in these `.bib` fields,
including `_`, `&`, `#`, and encodings such as `%20`, without LaTeX escapes:

```bibtex
userb = {https://your-site.example/code?file=src_main.py&tag=cv%20test#usage},
```

Contacts in `config/profile.tex` still use the LaTeX escaping rules above.

## Check and package

```bash
python3 -m pip install -r requirements-qa.txt
python3 scripts/check.py
python3 scripts/smoke.py
python3 scripts/pack.py
```

Builds reject text overflow, missing glyphs, unresolved references, and Biber
warnings in the final logs. Publication lint uses Biber's parser to check
required fields, dates, duplicate DOIs, and resource-link syntax; it does
not verify identifiers or link reachability online. Run `scripts/lint.py` separately
when needed.

PDF checks use actual layout metadata for margins, page numbers, blank
pages, headings, configured contact/resource targets, bookmarks, and language.
They reject link rectangles outside the margins and overlapping click areas
with different targets.
They also require embedded Unicode maps for standard CJK fonts and verify
Chinese text with a second PDF parser. Smoke checks reject a regression fixture
whose CJK maps have been removed.
Use `--language en` or `--language zh` to check one language.
The independent smoke fixtures cover long/special-character contacts, CJK,
empty sections, icon switches and missing-package fallback,
author marks, Chinese names and truncation, punctuation at line edges,
wrapping section headings kept with their first entries,
malformed data, failed-build preservation, and stale-package rejection.
Resource fixtures cover all eight optional-field subsets, whole-link wrapping
in narrow rows, separator spacing, icon fallback, long DOI/URL fields, and exact query/fragment URLs.
They also verify rejection of overlapping or out-of-bounds link annotations.
Test project copies are created in the cache, leaving profile content untouched.
Visual review of final pages is still required.

`scripts/check.py --sample` additionally checks the supplied fictional data;
use the ordinary check after replacing it with personal information.

The default archive is `dist/academic-cv.zip`.
Packaging requires both language PDFs to match the current source and recorded checksums.
After rebuilding only one language, rebuild both if the other is stale.
The ZIP contains source files, documentation, example PDFs, the build manifest,
and licences. Build caches are excluded. GitHub Actions compiles and checks the project
without publishing the CV.

## Attribution

The layout follows [Normal Resume](https://github.com/DELONG-L/Normal_Resume).
The modular structure and bibliography approach are inspired by
[Simple-CV](https://github.com/dcetin/Simple-CV). Academic section coverage
draws on [Academic CV by Diego](https://github.com/damascenodiego/Academic-CV-by-Diego)
and [academistral-cv](https://github.com/beyefendi/academistral-cv), without
copying their source code. See [NOTICE.md](NOTICE.md) and `licenses/`.

MIT licensed.
