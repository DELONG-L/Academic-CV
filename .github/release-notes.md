Download **academic-cv.zip** for editable LaTeX sources, English and Chinese
examples, example PDFs, documentation, and licences.

- **Overleaf:** upload the ZIP as a new project. Select **TeX Live 2026** and
  **XeLaTeX**, then choose `main.tex` for English or `main-zh.tex` for Chinese.
- **Local:** extract the ZIP and use an updated **TeX Live 2026** installation
  (LaTeX kernel 2026-06-01 or newer). Run `latexmk -xelatex main.tex` or
  `latexmk -xelatex main-zh.tex`. The README also describes the Python build,
  which embeds CJK Unicode maps for PDF viewer compatibility.
- Edit `config/profile.tex` or `config/profile-zh.tex`, the files in `content/`,
  and the corresponding bibliography in `data/` to write your own CV.
- For typography, entry layout, and publication fields, use the English guide
  in `docs/guide.md` or the Chinese guide in `docs/guide.zh-CN.md`.

The supplied people, institutions, and publications are fictional examples.
