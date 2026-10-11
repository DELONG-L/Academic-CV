# Source and implementation notes

This document records attribution for maintaining and redistributing the template.

## Simple-CV

- Repository: https://github.com/dcetin/Simple-CV
- Reviewed revision: `c43f219336824bbaaa0be2fa31e6c1a611395156`
- License: MIT, copyright 2020 Doruk Çetin.
- Used for: separate content files, BibLaTeX publications,
  author-name highlighting, and total-page footers.
- Original notice: `licenses/Simple-CV-MIT.txt`.

## Academic section references

- https://github.com/damascenodiego/Academic-CV-by-Diego
- https://github.com/beyefendi/academistral-cv

These repositories informed section coverage only. Their source code, sample
personal information, and publication records are not included in this project.

## New implementation

`academic-cv.cls` implements wrapping entry headers, delayed section headings,
explicit publication-status categories and optional resource
links. It also implements measured entry headings, optional monochrome icons,
explicit author-role marks, PDF bookmarks, and document language metadata.
It also implements Chinese typography, explicit CJK author-name formatting,
and independent Simplified Chinese example content with English publications.
Chinese section and entry weights, matched Latin font families, CJK/Latin
spacing, and punctuation at fixed margins are implemented in the class;
the typography fixture checks inline emphasis and baseline alignment.
The build, data lint, PDF checks, smoke fixture, packaging scripts, documentation,
and fictional example content were written for this project.

Fonts are loaded from the user's TeX distribution. Font files are not redistributed.

## Adobe character maps

The local build embeds missing standard CJK Unicode maps from TeX Live's Adobe
mapping resources into the PDF. The original copyright and licence remain in
each embedded map stream. The licence is also reproduced in
`licenses/Adobe-CMaps-BSD.txt`. These maps are separate from the template's MIT
licence; font binaries and TeX Live source are not vendored.

The optional icon package is loaded from the TeX distribution:

- Font Awesome 5 Free: https://ctan.org/pkg/fontawesome5. Font licence: SIL OFL 1.1;
  LaTeX package licence: LPPL 1.3c.

The MIT licence for this project's source does not replace the licences of
this dependency. Its source and standalone font files are not vendored.
