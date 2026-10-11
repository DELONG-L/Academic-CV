<div align="center">

<h1>Academic CV</h1>

<p>简洁的 LaTeX 学术简历模板。<br>中英文排版 · 衬线字体 · BibLaTeX 论文管理</p>

<p>
  <a href="https://github.com/DELONG-L/Academic-CV/actions/workflows/build.yml"><img src="https://github.com/DELONG-L/Academic-CV/actions/workflows/build.yml/badge.svg?branch=main" alt="自动构建状态"></a>
  <a href="https://github.com/DELONG-L/Academic-CV/releases/latest"><img src="https://img.shields.io/github/v/release/DELONG-L/Academic-CV?label=release&amp;color=333333" alt="最新版本"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-333333" alt="MIT 许可"></a>
</p>

<p>
  <a href="https://github.com/DELONG-L/Academic-CV/releases/latest/download/academic-cv.zip"><strong>下载源码 ZIP</strong></a>
  · <a href="docs/guide.zh-CN.md">使用指南</a>
  · <a href="README.md">English</a>
</p>

</div>

## 预览

单栏、居中姓名、横线分节与右侧日期。点击第一页预览，可打开完整的三页 PDF。

<p align="center"><a href="dist/cv-zh.pdf"><img src="docs/previews/cv-zh.png" alt="简体中文学术 CV 第一页" width="560"></a></p>

[中文 PDF](dist/cv-zh.pdf) · [英文 PDF](dist/cv.pdf)

示例中的人物、机构、论文和经历均为虚构，用于展示格式。

## 功能

| 功能 | 支持内容 |
|---|---|
| 双语排版 | 中英文示例、配套字体，以及中文行距、字重和中英混排间隔。 |
| 学术成果 | BibLaTeX 论文列表、本人姓名加粗、J/C/P 编号及出版或预印本链接。 |
| 模块化内容 | 教育、科研、教学、服务、资助等栏目分别维护，可调整顺序。 |
| 多页简历 | 自然分页、长条目换行、PDF 书签与总页数。 |
| 简洁样式 | 衬线正文、克制的横线、右侧日期及可选的单色图标。 |
| 便于使用 | TeX Live 自带字体、本地与 Overleaf 构建，以及现成源码 ZIP。 |

## 开始使用

### Overleaf

1. [下载 academic-cv.zip](https://github.com/DELONG-L/Academic-CV/releases/latest/download/academic-cv.zip)。
2. 在 Overleaf 中选择 **New Project → Upload Project**，上传 ZIP。
3. 在项目设置中选择 **TeX Live 2026** 和 **XeLaTeX** 编译器。
4. 英文选择 `main.tex`，中文选择 `main-zh.tex`，然后把示例替换为自己的资料。

ZIP 包含可编辑源码、中英文示例、PDF、说明和许可证。在 Overleaf 上使用不需要安装 Git 或 Python。

### 本地

解压同一个 ZIP，在项目文件夹中打开终端。需要更新后的 **TeX Live 2026**，
包含 2026-06-01 或更新的 LaTeX 内核、XeLaTeX、Biber、latexmk 和中文支持。

```bash
latexmk -xelatex main.tex
latexmk -xelatex main-zh.tex
```

安装、Git 克隆和不同系统的设置方法见[本地构建指南](docs/guide.zh-CN.md#快速开始)。

<details>
<summary>使用 Python 构建，改善中文 PDF 阅读器兼容性</summary>

Python 构建会补全中文字体的标准 Unicode 字符映射，使显示、搜索和复制中文不依赖阅读器额外加载字符映射。
生成文件为 `dist/cv.pdf` 和 `dist/cv-zh.pdf`。

需要 Python 3.10 或更新版本：

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements-build.txt
python3 scripts/build.py
```

Windows 下改用 `.venv\Scripts\activate` 激活环境。

</details>

## 换成自己的资料

| 修改内容 | 英文 | 中文 |
|---|---|---|
| 姓名与联系方式 | [config/profile.tex](config/profile.tex) | [config/profile-zh.tex](config/profile-zh.tex) |
| 经历与成果 | [content/](content/) | [content/zh/](content/zh/) |
| 栏目顺序 | [content/sections.tex](content/sections.tex) | [content/zh/sections.tex](content/zh/sections.tex) |
| 论文资料 | [data/publications.bib](data/publications.bib) | [data/publications-zh.bib](data/publications-zh.bib) |

两个示例共用 [config/style.tex](config/style.tex)，用于调整字体、间距、页边距、颜色和图标。
类文件为 `academic-cv.cls`，通过 `\documentclass{academic-cv}` 加载。

[使用指南](docs/guide.zh-CN.md)说明联系方式、中英混排、条目布局、论文字段、作者姓名加粗，以及检查和打包方法。

## 项目来源与许可

项目采用 MIT 许可。模块化和论文管理思路借鉴 [Simple-CV](https://github.com/dcetin/Simple-CV)。
学术栏目参考 [Academic CV by Diego](https://github.com/damascenodiego/Academic-CV-by-Diego)
与 [academistral-cv](https://github.com/beyefendi/academistral-cv)，未复制这两个项目的源码。
来源与第三方许可声明见 [NOTICE.md](NOTICE.md) 和 [licenses/](licenses/)。
