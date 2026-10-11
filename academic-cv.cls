\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{academic-cv}[2026/10/11 v2.6 Academic CV]

% Layout derived from DELONG-L/Normal_Resume (MIT).
% Modular CV and bibliography conventions inspired by dcetin/Simple-CV (MIT).
% Original copyright notices are retained in licenses/. See NOTICE.md.

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass[11pt,a4paper]{article}

\RequirePackage{iftex}
\ifXeTeX\else
  \ClassError{academic-cv}{XeLaTeX is required}{Select XeLaTeX in Overleaf or use scripts/build.py.}
\fi
\RequirePackage{fontspec}
\RequirePackage{xeCJK}
% File names work even when macOS has not registered TeX fonts by family name.
\newcommand{\cv@settermes}{%
  \setmainfont{texgyretermes-regular.otf}[
    BoldFont=texgyretermes-bold.otf,ItalicFont=texgyretermes-italic.otf,
    BoldItalicFont=texgyretermes-bolditalic.otf]%
}
\cv@settermes
\setsansfont{texgyreheros-regular.otf}[Scale=MatchLowercase,
  BoldFont=texgyreheros-bold.otf,ItalicFont=texgyreheros-italic.otf,
  BoldItalicFont=texgyreheros-bolditalic.otf]
% Chinese headings need the full Latin cap height; body sans fonts keep their
% original x-height matching. This selector affects Chinese headings only.
\newfontfamily\cv@chinesesans{texgyreheros-regular.otf}[Scale=1,
  BoldFont=texgyreheros-bold.otf,ItalicFont=texgyreheros-italic.otf,
  BoldItalicFont=texgyreheros-bolditalic.otf]
\setmonofont{texgyrecursor-regular.otf}[Scale=MatchLowercase,
  BoldFont=texgyrecursor-bold.otf,ItalicFont=texgyrecursor-italic.otf,
  BoldItalicFont=texgyrecursor-bolditalic.otf]
\setCJKmainfont{FandolSong-Regular.otf}[BoldFont=FandolSong-Bold.otf,
  ItalicFont=FandolKai-Regular.otf,BoldItalicFont=FandolKai-Regular.otf]
\setCJKsansfont{FandolHei-Regular.otf}[BoldFont=FandolHei-Bold.otf]
\setCJKmonofont{FandolFang-Regular.otf}
% Keep punctuation compact without protruding into the CV's fixed margins.
\xeCJKDeclarePunctStyle{academic-cv}{%
  fixed-punct-ratio=.5,mixed-punct-ratio=1.0,kerning-total-ratio=.5,
  bound-punct-ratio=1.0,enabled-hanging=false,
  optimize-kerning=true,optimize-margin=false}

\RequirePackage[english]{babel}
\RequirePackage{geometry}
\geometry{left=20mm,right=20mm,top=18mm,bottom=21mm,footskip=10mm}
\RequirePackage{xcolor}
\definecolor{cvaccent}{HTML}{000000}
\definecolor{cvmuted}{HTML}{424242}
\RequirePackage{microtype}
\RequirePackage{titlesec}
\RequirePackage{enumitem}
\RequirePackage{tabularx}
\RequirePackage{needspace}
\RequirePackage{etoolbox}
\RequirePackage{lastpage}
\RequirePackage{fancyhdr}
\RequirePackage{xparse}
\RequirePackage[unicode,hidelinks,breaklinks]{hyperref}
\RequirePackage{xurl}
\RequirePackage{bookmark}
\urlstyle{same}
\Urlmuskip=0mu plus 1mu
\setlength{\parindent}{0pt}
\setlength{\parskip}{3pt}
\setlength{\emergencystretch}{1.5em}
\raggedbottom

\newif\ifcv@chinese
\newcommand{\cv@cjkentryfamily}{serif}
\newcommand{\cv@cjklatingap}{.20em}
\newcommand{\cv@sectionfont}{%
  \ifcv@chinese\fontsize{12}{15}\selectfont\else\large\fi}
\newcommand{\cv@sectionstyle}{%
  \ifcv@chinese
    \cv@chinesesans\mdseries\CJKfamily{\CJKsfdefault}%
    \xeCJKsetup{CJKglue={\hskip.04em\relax}}%
  \else\scshape\fi}
\newcommand{\cv@entrytitlestyle}{%
  \bfseries\ifcv@chinese
    \ifdefstring{\cv@cjkentryfamily}{sans}%
      {\cv@chinesesans\CJKfamily{\CJKsfdefault}}{\rmfamily\CJKfamily{\CJKrmdefault}}%
  \fi}
\newcommand{\cv@institutionstyle}{\ifcv@chinese\upshape\else\itshape\fi}
% Dates, locations, and short roles share one secondary text style in both
% languages, including when a long entry switches to a stacked layout.
% textcolor starts horizontal mode before adding color, preserving the first
% baseline in paragraph table cells and their measured height for auto layout.
\newcommand{\cv@metatext}[1]{{\small\mdseries\upshape\textcolor{cvmuted}{#1}}}
\titleformat{\section}
  {\cv@sectionfont\cv@sectionstyle\raggedright\color{cvaccent}}{}{0pt}{\cv@sectionbookmark}
  [\vspace{2pt}{\color{cvaccent!55!white}\titlerule[.3pt]}]
\newlength{\cv@sectionbefore}
\newlength{\cv@sectionafter}
\newlength{\cv@entrygap}
\newlength{\cv@bibgap}
\setlength{\cv@sectionbefore}{14pt}
\setlength{\cv@sectionafter}{5.5pt}
\setlength{\cv@entrygap}{6pt}
\setlength{\cv@bibgap}{6pt}
\titlespacing*{\section}{0pt}{\cv@sectionbefore}{\cv@sectionafter}
\newlist{cvitems}{itemize}{1}
\setlist[cvitems]{label=\textbullet,leftmargin=1.25em,
  topsep=2pt,itemsep=1pt,parsep=0pt,partopsep=0pt}

% Contact fields are optional. Empty fields do not produce separators.
\newcommand{\cv@name}{Firstname Lastname}
\newcommand{\cv@position}{}
\newcommand{\cv@affiliation}{}
\newcommand{\cv@email}{}
\newcommand{\cv@phone}{}
\newcommand{\cv@website}{}
\newcommand{\cv@websitelabel}{}
\newcommand{\cv@orcid}{}
\newcommand{\cv@github}{}
\newcommand{\cv@githublabel}{}
\newcommand{\cv@linkedin}{}
\newcommand{\cv@linkedinlabel}{LinkedIn}
\newcommand{\cv@scholar}{}
\newcommand{\cv@scholarlabel}{Google Scholar}
\newcommand{\cv@location}{}
\newcommand{\cv@updated}{}
\newcommand{\cv@footername}{}
\newcommand{\cv@language}{en-GB}
\newcommand{\cv@linespread}{}
\newcommand{\cv@icons}{minimal}
\newcommand{\cv@entrylayout}{auto}
\newif\ifcv@iconfont
\newif\ifcv@accsupp
\newlength{\cv@datewidth}
\setlength{\cv@datewidth}{33mm}
\newlength{\cv@stackthreshold}
\setlength{\cv@stackthreshold}{3.5\baselineskip}
\newsavebox{\cv@entrybox}
\newlength{\cv@entryreserve}

\ExplSyntaxOn
% URL data is stored as characters, independently of TeX's math/alignment
% catcodes. Conventional escapes are accepted as well as a bare underscore.
\cs_new_protected:Npn \cv_set_uri:Nn #1#2
  {
    \tl_set:Nn \l_tmpa_tl {#2}
    \tl_trim_spaces:N \l_tmpa_tl
    \tl_replace_all:Nnn \l_tmpa_tl {\_} {_}
    \tl_replace_all:Nnn \l_tmpa_tl {\&} {&}
    \tl_replace_all:NnV \l_tmpa_tl {\%} \c_percent_str
    \tl_replace_all:NnV \l_tmpa_tl {\#} \c_hash_str
    \tl_set:Nx #1 {\tl_to_str:V \l_tmpa_tl}
  }
\cs_new_protected:Npn \cv_uri_display:N #1
  {\exp_args:NV \nolinkurl #1}
\cs_new_protected:Npn \cv_website_display:
  {
    \regex_extract_once:nVNTF {\A https?:// ([^/?\x{23}]+)}
      \cv@website \l_tmpa_seq
      {
        \tl_set:Nx \l_tmpb_tl {\seq_item:Nn \l_tmpa_seq {2}}
        \cv_uri_display:N \l_tmpb_tl
      }
      {\cv_uri_display:N \cv@website}
  }
\cs_new_protected:Npn \cv_github_display:
  {
    \tl_set_eq:NN \l_tmpb_tl \cv@github
    \regex_replace_once:nnN {\A https?://} {} \l_tmpb_tl
    \cv_uri_display:N \l_tmpb_tl
  }
\cs_new_eq:NN \cv@uridisplay \cv_uri_display:N
\cs_new_eq:NN \cv@websitedisplay \cv_website_display:
\cs_new_eq:NN \cv@githubdisplay \cv_github_display:
\keys_define:nn {academic-cv/profile}
  {
    name .code:n = \def\cv@name{#1},
    position .code:n = \def\cv@position{#1},
    affiliation .code:n = \def\cv@affiliation{#1},
    email .code:n = \cv_set_uri:Nn \cv@email {#1},
    phone .code:n = \def\cv@phone{#1},
    website .code:n = \cv_set_uri:Nn \cv@website {#1},
    website-label .code:n = \def\cv@websitelabel{#1},
    orcid .code:n = \cv_set_uri:Nn \cv@orcid {#1},
    github .code:n = \cv_set_uri:Nn \cv@github {#1},
    github-label .code:n = \def\cv@githublabel{#1},
    linkedin .code:n = \cv_set_uri:Nn \cv@linkedin {#1},
    linkedin-label .code:n = \def\cv@linkedinlabel{#1},
    scholar .code:n = \cv_set_uri:Nn \cv@scholar {#1},
    scholar-label .code:n = \def\cv@scholarlabel{#1},
    location .code:n = \def\cv@location{#1},
    updated .code:n = \def\cv@updated{#1},
    footer-name .code:n = \def\cv@footername{#1},
    language .code:n = \def\cv@language{#1}
  }
\keys_define:nn {academic-cv/style}
  {
    accent .code:n = \definecolor{cvaccent}{HTML}{#1},
    date-width .code:n = \setlength{\cv@datewidth}{#1},
    main-font .code:n = \str_if_eq:nnTF {#1}{TeX~Gyre~Termes}
      {\cv@settermes}{\setmainfont{#1}},
    cjk-font .code:n = \setCJKmainfont{#1},
    cjk-sans-font .code:n = \setCJKsansfont{#1},
    cjk-entry-family .choice:,
    cjk-entry-family / serif .code:n = \def\cv@cjkentryfamily{serif},
    cjk-entry-family / sans .code:n = \def\cv@cjkentryfamily{sans},
    cjk-latin-gap .code:n =
      \dim_compare:nNnTF {#1} < {0pt}
        {\ClassError{academic-cv}{cjk-latin-gap~must~not~be~negative}{Use~a~length~such~as~.20em.}}
        {\def\cv@cjklatingap{#1}},
    line-spread .code:n =
      \fp_compare:nNnTF {#1} > {0}
        {\def\cv@linespread{#1}}
        {\ClassError{academic-cv}{line-spread~must~be~positive}{Use~a~positive~number.}},
    margins .code:n = \geometry{#1},
    icons .choice:,
    icons / none .code:n = \def\cv@icons{none},
    icons / minimal .code:n = \def\cv@icons{minimal},
    entry-layout .choice:,
    entry-layout / auto .code:n = \def\cv@entrylayout{auto},
    entry-layout / columns .code:n = \def\cv@entrylayout{columns},
    entry-layout / stacked .code:n = \def\cv@entrylayout{stacked},
    stack-threshold .code:n = \setlength{\cv@stackthreshold}{#1},
    density .choice:,
    density / classic .code:n =
      {
        \setlength{\cv@sectionbefore}{14pt}
        \setlength{\cv@sectionafter}{5.5pt}
        \setlength{\cv@entrygap}{6pt}
        \setlength{\cv@bibgap}{6pt}
        \setlength{\parskip}{3pt}
        \setlist[cvitems]{label=\textbullet,leftmargin=1.25em,
          topsep=2pt,itemsep=1pt,parsep=0pt,partopsep=0pt}
      },
    density / compact .code:n =
      {
        \setlength{\cv@sectionbefore}{12pt}
        \setlength{\cv@sectionafter}{4.5pt}
        \setlength{\cv@entrygap}{5pt}
        \setlength{\cv@bibgap}{5pt}
        \setlength{\parskip}{2pt}
        \setlist[cvitems]{label=\textbullet,leftmargin=1.25em,
          topsep=2pt,itemsep=.8pt,parsep=0pt,partopsep=0pt}
      },
    max-authors .code:n =
      {
        \int_compare:nNnTF {#1} > {0}
          {\ExecuteBibliographyOptions{maxbibnames=#1,minbibnames=#1}}
          {\ClassError{academic-cv}{max-authors~must~be~positive}{Use~an~integer~of~at~least~1.}}
      },
    author-names .choice:,
    author-names / initials .code:n = \ExecuteBibliographyOptions{giveninits=true},
    author-names / full .code:n = \ExecuteBibliographyOptions{giveninits=false}
  }
\NewDocumentCommand{\CVSetup}{m}{\keys_set:nn {academic-cv/profile}{#1}}
\NewDocumentCommand{\CVStyle}{m}{\keys_set:nn {academic-cv/style}{#1}}
\cs_new_protected:Npn \cv_apply_language:
  {
    \regex_match:nVTF {\A zh (?: - | \Z)} \cv@language
      {\cv@chinesetrue}{\cv@chinesefalse}
    \tl_if_empty:NTF \cv@linespread
      {\ifcv@chinese\linespread{1.15}\fi}
      {\exp_args:NV \linespread \cv@linespread}
    \ifcv@chinese
      \xeCJKsetup{
        CJKecglue={\hskip\cv@cjklatingap\relax},
        xCJKecglue=true,PunctStyle=academic-cv,CheckSingle=true}
    \fi
  }
\cs_new_eq:NN \cv@applylanguage \cv_apply_language:
\ExplSyntaxOff

% These are optional dependencies. Their absence keeps the text labels.
\AtEndPreamble{%
  \cv@applylanguage
  \hypersetup{pdflang={\cv@language}}%
  \setlength{\bibitemsep}{\cv@bibgap}%
  \ifdefstring{\cv@icons}{none}{}{%
    \IfFileExists{fontawesome5.sty}{%
      \RequirePackage{fontawesome5}\cv@iconfonttrue
    }{\ClassWarning{academic-cv}{fontawesome5 unavailable; using text labels}}%
    \IfFileExists{accsupp.sty}{%
      \RequirePackage{accsupp}\cv@accsupptrue
    }{}%
  }%
}
\newcommand{\cv@icon}[2][\footnotesize]{%
  \ifcv@iconfont
    \ifcv@accsupp\BeginAccSupp{method=escape,ActualText={}}\fi
    {#1\textcolor{cvmuted}{%
      \ifstrequal{#2}{scholar}{%
        \faIcon{graduation-cap}%
      }{\faIcon{#2}}}}%
    \ifcv@accsupp\EndAccSupp{}\fi
    \nobreak\hspace{.35em}%
  \fi
}

% Machine-readable build information is written to a sidecar, never to
% the visible CV. Checks use the actual geometry and rendered link targets.
\newwrite\cv@metafile
\newcommand{\cv@meta}[1]{\immediate\write\cv@metafile{#1}}
\AtBeginDocument{%
  \ifdim\cv@datewidth<1pt
    \ClassError{academic-cv}{date-width is too small}{Use a positive date column width.}%
  \fi
  \ifdefstring{\cv@entrylayout}{stacked}{}{%
  \ifdim\cv@datewidth>.45\textwidth
    \ClassError{academic-cv}{date-width exceeds 45 percent of the text width}%
      {Use a narrower date column or entry-layout=stacked.}%
  \fi}%
  \immediate\openout\cv@metafile=\jobname.cvmeta
  \cv@meta{page-width=\the\paperwidth}%
  \cv@meta{page-height=\the\paperheight}%
  \cv@meta{left=\the\dimexpr1in+\hoffset+\oddsidemargin\relax}%
  \cv@meta{right=\the\dimexpr\paperwidth-1in-\hoffset-\oddsidemargin-\textwidth\relax}%
  \cv@meta{body-top=\the\dimexpr1in+\voffset+\topmargin+\headheight+\headsep\relax}%
  \cv@meta{body-bottom=\the\dimexpr1in+\voffset+\topmargin+\headheight+\headsep+\textheight\relax}%
  \cv@meta{language=\cv@language}%
  \cv@meta{orcid=\cv@orcid}%
}
\AtEndDocument{\immediate\closeout\cv@metafile}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\fancyfoot[L]{\footnotesize\parbox[b]{\dimexpr\textwidth-18mm\relax}{%
  \raggedright\color{cvmuted}%
  \ifdefempty{\cv@footername}{\cv@name}{\cv@footername}%
  \ifdefempty{\cv@updated}{}{\quad\cv@updated}}}
\fancyfoot[R]{\footnotesize\color{cvmuted}\thepage\,/\,\pageref*{LastPage}}

% The separator disappears at a line break. Explicit box spacing survives
% xeCJK's treatment of ordinary spaces around a font or language change.
\newcommand{\cv@linksep}{%
  \discretionary{}{}{\hbox{%
    \hskip.5em\relax\textcolor{cvmuted}{\textbullet}\hskip.5em\relax}}%
}
\newcommand{\cv@contactsep}{}
\newcommand{\cv@contact}[1]{%
  \cv@contactsep#1\gdef\cv@contactsep{\cv@linksep}%
}
% Separate header rows by their text boxes, without body paragraph glue or
% the baseline spacing of the preceding font affecting the gap.
\newcommand{\cv@headerrowgap}{\par\nointerlineskip\vspace{6pt}}
\NewDocumentCommand{\CVHeader}{}{%
  \ifcv@chinese
    \hypersetup{pdftitle={\cv@name\space-- 学术简历},
      pdfauthor={\cv@name},pdfsubject={学术简历}}%
  \else
    \hypersetup{pdftitle={\cv@name\space-- Curriculum Vitae},
      pdfauthor={\cv@name},pdfsubject={Academic curriculum vitae}}%
  \fi
  \begingroup
  \centering
  \setlength{\parskip}{0pt}%
  {\ifcv@chinese\fontsize{22}{29}\selectfont\cv@chinesesans\bfseries\CJKfamily{\CJKsfdefault}%
     \xeCJKsetup{CJKglue={\hskip.04em\relax}}%
   \else\fontsize{25}{28}\selectfont\scshape\fi
   \color{cvaccent}\cv@name\par}%
  % A compact subtitle wraps naturally when a long profile needs more space.
  \ifboolexpr{test {\ifdefempty{\cv@position}} and test {\ifdefempty{\cv@affiliation}}}{}{%
    \cv@headerrowgap%
    {\small
      \cv@position%
      \ifdefempty{\cv@position}{}{\ifdefempty{\cv@affiliation}{}{\cv@linksep}}%
      \cv@affiliation\par}%
  }%
  \cv@headerrowgap%
  \gdef\cv@contactsep{}%
  {\small
    % Wrapped contacts can have taller PDF link rectangles than their TeX
    % glyph boxes. Keep click areas on consecutive lines separate.
    \ifdim\baselineskip<1.45em\relax\setlength{\baselineskip}{1.45em}\fi
    \ifdefempty{\cv@email}{}{%
      \cv@meta{contact=mailto:\cv@email}%
      \cv@contact{\cv@icon{envelope}\href{mailto:\cv@email}{\cv@uridisplay\cv@email}}}%
    \ifdefempty{\cv@website}{}{\cv@contact{\href{\cv@website}{%
      \cv@icon{globe}%
      \ifdefempty{\cv@websitelabel}{\cv@websitedisplay}{\cv@websitelabel}}}%
      \cv@meta{contact=\cv@website}}%
    \ifdefempty{\cv@scholar}{}{%
      \cv@meta{contact=\cv@scholar}%
      \cv@contact{\cv@icon{scholar}\href{\cv@scholar}{\cv@scholarlabel}}}%
    \ifdefempty{\cv@orcid}{}{%
      \cv@meta{contact=https://orcid.org/\cv@orcid}%
      \cv@contact{\cv@icon{orcid}\href{https://orcid.org/\cv@orcid}{ORCID: \cv@uridisplay\cv@orcid}}}%
    \ifdefempty{\cv@phone}{}{\cv@contact{\cv@icon{phone}\cv@phone}}%
    \ifdefempty{\cv@location}{}{\cv@contact{\cv@icon{map-marker-alt}\cv@location}}%
    \ifdefempty{\cv@github}{}{\cv@contact{\href{\cv@github}{%
      \cv@icon{github}%
      \ifdefempty{\cv@githublabel}{\cv@githubdisplay}{\cv@githublabel}}}%
      \cv@meta{contact=\cv@github}}%
    \ifdefempty{\cv@linkedin}{}{\cv@contact{\href{\cv@linkedin}{%
      \cv@icon{linkedin-in}%
      \ifdefempty{\cv@linkedinlabel}{LinkedIn}{\cv@linkedinlabel}}}%
      \cv@meta{contact=\cv@linkedin}}%
    \par
  }%
  \endgroup
  \vspace{3pt}
}

% Headings are delayed until content is printed, so empty sections stay hidden.
\newcommand{\cv@pendingsection}{}
\newif\ifcv@sectionnewpage
\newsavebox{\cv@sectionbox}
\newcounter{cv@section}
\newcommand{\cv@sectionbookmark}{%
  \ifdefempty{\cv@pendingsection}{}{%
    \pdfbookmark[0]{\cv@pendingsection}{cv.section.\arabic{cv@section}}%
  }%
}
\NewDocumentCommand{\CVSection}{m}{%
  \global\cv@sectionnewpagefalse\gdef\cv@pendingsection{#1}}
\newcommand{\cv@ensuresection}[1][3\baselineskip]{%
  \ifdefempty{\cv@pendingsection}{}{%
    % Apply an editorial page break only when this section prints content.
    % Empty sections therefore cannot create a page break or blank page.
    \ifcv@sectionnewpage\par\newpage\fi
    \global\cv@sectionnewpagefalse
    % Measure wrapping headings without emitting their bookmark. The extra
    % baseline covers the rule, paragraph glue, and the first-entry transition.
    \setbox\cv@sectionbox=\vbox{%
      \hsize=\linewidth\cv@sectionfont\cv@sectionstyle\raggedright
      \noindent\cv@pendingsection\par}%
    \par\Needspace{\dimexpr#1+\cv@sectionbefore+\cv@sectionafter
      +\ht\cv@sectionbox+\dp\cv@sectionbox+\baselineskip\relax}%
    \stepcounter{cv@section}%
    \cv@meta{section=\arabic{cv@section}}%
    \section*{\cv@pendingsection}%
    \gdef\cv@pendingsection{}%
  }%
}
\NewDocumentCommand{\CVIncludeSection}{s m m}{%
  \CVSection{#2}%
  \IfBooleanT{#1}{\global\cv@sectionnewpagetrue}%
  \InputIfFileExists{#3}{}{%
    \ClassError{academic-cv}{Missing section file '#3'}{Check content/sections.tex.}%
  }%
  \gdef\cv@pendingsection{}%
  \global\cv@sectionnewpagefalse
}

% The heading is a short, wrapping table; the description remains ordinary
% text so long descriptions can break across pages.
\newcommand{\cv@columnheading}[4]{%
  \begin{tabularx}{\linewidth}{@{}>{\raggedright\arraybackslash}X
    @{\hspace{1em}}>{\raggedleft\arraybackslash}p{\cv@datewidth}@{}}
    {\cv@entrytitlestyle#1} & {\cv@metatext{#2}}%
    \ifboolexpr{test {\ifblank{#3}} and test {\ifblank{#4}}}{}{%
      \\ {\cv@institutionstyle#3} & {\cv@metatext{#4}}%
    }%
  \end{tabularx}%
}
\newcommand{\cv@stackedheading}[4]{%
  \begin{minipage}{\linewidth}
    {\cv@entrytitlestyle#1}\par
    \ifblank{#3}{}{{\cv@institutionstyle#3}\par}%
    \ifboolexpr{test {\ifblank{#2}} and test {\ifblank{#4}}}{}{%
      {\cv@metatext{#2%
        \ifblank{#4}{}{\ifblank{#2}{}{\quad}#4}}\par}%
    }%
  \end{minipage}%
}
\NewDocumentCommand{\CVEntry}{m m m m +m}{%
  \begingroup
  \setlength{\tabcolsep}{0pt}%
  \renewcommand{\arraystretch}{1.04}%
  \ifdefstring{\cv@entrylayout}{stacked}{%
    \sbox{\cv@entrybox}{\cv@stackedheading{#1}{#2}{#3}{#4}}%
  }{%
    \sbox{\cv@entrybox}{\cv@columnheading{#1}{#2}{#3}{#4}}%
    \ifdefstring{\cv@entrylayout}{auto}{%
      \ifdim\dimexpr\ht\cv@entrybox+\dp\cv@entrybox\relax>\cv@stackthreshold
        \sbox{\cv@entrybox}{\cv@stackedheading{#1}{#2}{#3}{#4}}%
      \fi
    }{}%
  }%
  \setlength{\cv@entryreserve}{\dimexpr\ht\cv@entrybox+\dp\cv@entrybox+.5\baselineskip\relax}%
  \ifblank{#5}{}{\addtolength{\cv@entryreserve}{\baselineskip}}%
  \ifdim\cv@entryreserve>.8\textheight
    \ClassError{academic-cv}{Entry heading is too tall}{Shorten the title or move details into the description.}%
  \fi
  \cv@ensuresection[\cv@entryreserve]%
  \par\Needspace{\cv@entryreserve}%
  \noindent\usebox{\cv@entrybox}\par
  \endgroup
  \ifblank{#5}{}{\nobreak#5\par}%
  \addvspace{\cv@entrygap}%
}
\NewDocumentCommand{\CVLine}{m m +m}{%
  \CVEntry{#1}{#2}{}{}{#3}%
}
\NewDocumentCommand{\CVParagraph}{+m}{%
  \cv@ensuresection\par#1\par%
}

% Bibliography groups are explicit; accepted work stays in its venue group.
\RequirePackage[backend=biber,style=numeric,datamodel=academic-cv,sorting=ydnt,defernumbers=true,
  giveninits=true,maxbibnames=99,minbibnames=99,
  doi=false,isbn=false,url=false,eprint=false]{biblatex}
\setlength{\bibitemsep}{\cv@bibgap}
\setlength{\bibparsep}{0pt}
% Keep the numeric hanging labels, but let CV headings own the vertical
% spacing instead of inheriting the article class's list top/bottom glue.
\defbibenvironment{bibliography}
  {\list
     {\printtext[labelnumberwidth]{%
        \printfield{labelprefix}\printfield{labelnumber}}}
     {\setlength{\labelwidth}{\labelnumberwidth}%
      \setlength{\leftmargin}{\labelwidth}%
      \setlength{\labelsep}{\biblabelsep}%
      \addtolength{\leftmargin}{\labelsep}%
      \setlength{\topsep}{0pt}%
      \setlength{\partopsep}{0pt}%
      \setlength{\itemsep}{\bibitemsep}%
      \setlength{\parsep}{\bibparsep}}%
      \renewcommand*{\makelabel}[1]{\hss##1}}
  {\endlist}
  {\item}
\renewcommand*{\bibfont}{%
  \normalsize
  % Keep wrapped resource rows and custom bibliography links separate.
  \ifdim\baselineskip<1.45em\relax\setlength{\baselineskip}{1.45em}\fi
}
% A short boxed resource link can move to the next line without forcing the
% preceding citation to stretch or extend beyond the bibliography margins.
\AtBeginBibliography{\raggedright}
\newcommand{\cv@selfgiven}{}
\newcommand{\cv@selffamily}{}
\newif\ifcv@cofirstshown
\newif\ifcv@correspondingshown
\newif\ifcv@cjkname
\NewDocumentCommand{\CVAuthorName}{m m}{%
  \def\cv@selfgiven{#1}\def\cv@selffamily{#2}%
}
\newcommand{\cv@formatname}[1]{%
  \ifitemannotation{highlight}{\mkbibbold{#1}}{%
    \ifboolexpr{test {\ifdefstrequal{\namepartgiven}{\cv@selfgiven}}
      and test {\ifdefstrequal{\namepartfamily}{\cv@selffamily}}}%
      {\mkbibbold{#1}}{#1}%
  }%
}
\renewcommand*{\mkbibnamegiven}[1]{\cv@formatname{#1}}
\newcommand{\cv@authormarks}{%
  \ifitemannotation{cofirst}{%
    \textsuperscript{\ensuremath{\dagger}}\global\cv@cofirstshowntrue}{}%
  \ifitemannotation{corresponding}{%
    \textsuperscript{*}\global\cv@correspondingshowntrue}{}%
}
\renewcommand*{\mkbibnamefamily}[1]{%
  \cv@formatname{#1}\ifcv@cjkname\else\cv@authormarks\fi}
\renewcommand*{\mkbibnameprefix}[1]{\cv@formatname{#1}}
\renewcommand*{\mkbibnamesuffix}[1]{\cv@formatname{#1}}

% Annotated CJK names retain their given names and print family first.
% The annotation is explicit: romanized names keep the ordinary name format.
\DeclareNameFormat{cv-author}{%
  \ifitemannotation{cjk}{%
    \cv@cjknametrue
    \ifnumgreater{\value{listcount}}{\value{liststart}}{、}{}%
    \usebibmacro{name:hook}{\namepartfamily\namepartgiven}%
    \mkbibcompletename{\mkbibnamefamily{\namepartfamily}%
      \mkbibnamegiven{\namepartgiven}\cv@authormarks}%
    \ifboolexpr{test {\ifnumequal{\value{listcount}}{\value{liststop}}}
      and test \ifmorenames}{等}{}%
  }{%
    \cv@cjknamefalse
    \ifgiveninits
      {\usebibmacro{name:given-family}{\namepartfamily}{\namepartgiveni}%
        {\namepartprefix}{\namepartsuffix}}%
      {\usebibmacro{name:given-family}{\namepartfamily}{\namepartgiven}%
        {\namepartprefix}{\namepartsuffix}}%
    \usebibmacro{name:andothers}%
  }%
}
\DeclareNameAlias{author}{cv-author}

% A Chinese-language publication can opt into upright venue names and omit
% English "In:" and page prefixes. English publications retain the native style.
\DeclareFieldFormat{journaltitle}{\ifkeyword{chinese}{#1}{\mkbibemph{#1}}}
\DeclareFieldFormat{booktitle}{\ifkeyword{chinese}{#1}{\mkbibemph{#1}}}
\DeclareFieldFormat{pages}{%
  \ifkeyword{chinese}{#1}{\mkpageprefix[bookpagination]{#1}}}
\renewbibmacro*{in:}{%
  \ifkeyword{chinese}{}{\printtext{\bibstring{in}\intitlepunct}}}

% Acceptance is a per-entry state, independent of the journal/conference group.
\newcommand{\cv@ifinpress}[2]{%
  \ifboolexpr{test {\iffieldequalstr{pubstate}{inpress}} or
    test {\iffieldequalstr{pubstate}{forthcoming}}}{#1}{#2}%
}
% Keep the state for link routing without printing a status label in the CV.
\renewbibmacro*{addendum+pubstate}{\printfield{addendum}}

\newcommand{\cv@declarepubgroup}[1]{%
  \DeclareBibliographyCategory{cv#1}%
  \newcounter{cvpub@#1}%
}
\forcsvlist{\cv@declarepubgroup}{journal,conference,preprint,underreview}
\newcounter{cvpub@groupcount}
\newcommand{\cv@addpub}[1]{%
  \addtocategory{cv#1}{\thefield{entrykey}}%
  \stepcounter{cvpub@#1}%
}
\newcommand{\cv@categorizepub}[1]{%
  \ifkeyword{#1}{%
    \stepcounter{cvpub@groupcount}%
    \cv@addpub{#1}%
  }{}%
}
\AtDataInput{%
  \setcounter{cvpub@groupcount}{0}%
  \forcsvlist{\cv@categorizepub}{journal,conference,preprint,underreview}%
  \ifnum\value{cvpub@groupcount}=1\relax\else
    \ClassError{academic-cv}{Publication '\thefield{entrykey}' needs exactly one group keyword}%
      {Set exactly one of journal, conference, preprint, or underreview in keywords.
       For accepted papers use journal or conference with pubstate=inpress.}%
  \fi
}
\newcounter{cv@pubgroup}
\defbibheading{cvgroup}[\refname]{%
  \cv@ensuresection
  \par\Needspace{4\baselineskip}%
  \stepcounter{cv@pubgroup}%
  \noindent\pdfbookmark[1]{#1}{cv.pubgroup.\arabic{cv@pubgroup}}%
  {\cv@entrytitlestyle#1}\par\nobreak\vspace{2pt}\nobreak%
}
\NewDocumentCommand{\CVPublicationGroup}{m m m}{%
  \ifcsdef{c@cvpub@#1}{%
    \ifnum\value{cvpub@#1}>0\relax
      \ifdefempty{\cv@pendingsection}{\par\addvspace{\cv@sectionbefore}}{}%
      \cv@ensuresection[4\baselineskip]%
      \begin{refcontext}[labelprefix=#3]
        \printbibliography[category=cv#1,heading=cvgroup,title={#2},resetnumbers=true]
      \end{refcontext}
    \fi
  }{\ClassError{academic-cv}{Unknown publication group '#1'}{Use journal, conference, preprint, or underreview.}}%
}
\NewDocumentCommand{\CVAuthorLegend}{}{%
  \ifboolexpr{bool {cv@cofirstshown} or bool {cv@correspondingshown}}{%
    \par\addvspace{\cv@entrygap}\Needspace{2\baselineskip}%
    {\small\color{cvmuted}%
      \ifcv@cofirstshown\textsuperscript{\ensuremath{\dagger}}\,%
        \ifcv@chinese 共同第一作者。\else Equal contribution.\fi\fi
      \ifcv@correspondingshown\quad\textsuperscript{*}\,%
        \ifcv@chinese 通讯作者。\else Corresponding author.\fi\fi
      \par}%
  }{}%
}
% Keep each short resource label and its icon in one clickable, unbroken unit;
% the complete resource row remains free to wrap between those units.
\newcommand{\cv@resourcelink}[3]{%
  \cv@meta{resource=#1}\mbox{%
    \small\color{cvmuted}%
    % dvipdfmx's Latin link rectangles can exceed the nominal line height.
    % Reserve enough height/depth for adjacent wrapped resource rows.
    \rule[-.45em]{0pt}{1.4em}%
    \href{#1}{\cv@icon[\scriptsize]{#2}#3}}%
}
% Pending publication takes priority over the venue group when choosing links.
\newcommand{\cv@ifpublished}[2]{%
  \cv@ifinpress{#2}{%
    \ifboolexpr{test {\ifkeyword{journal}} or test {\ifkeyword{conference}}}{#1}{#2}}%
}
\newcommand{\cv@publisherlabel}{\ifcv@chinese 出版页\else Publisher\fi}
\newcommand{\cv@preprintlabel}{\ifcv@chinese 预印本\else Preprint\fi}
\DeclareFieldFormat{cv:paperpage}{\cv@resourcelink{#1}{external-link-alt}{%
  \cv@ifpublished{\cv@publisherlabel}{\cv@preprintlabel}}}
\DeclareFieldAlias{usera}{cv:paperpage}
\DeclareFieldFormat{cv:doi}{%
  \cv@resourcelink{https://doi.org/#1}{external-link-alt}{\cv@publisherlabel}}
\DeclareFieldFormat{cv:arxiv}{%
  \cv@resourcelink{https://arxiv.org/abs/#1}{external-link-alt}{arXiv}}
\DeclareFieldFormat{userb}{\cv@resourcelink{#1}{code}{%
  \ifcv@chinese 代码\else Code\fi}}
\DeclareFieldFormat{userc}{\cv@resourcelink{#1}{external-link-alt}{%
  \ifcv@chinese 项目\else Project\fi}}
\newbibmacro*{cv:paperpage}{%
  \iffieldundef{url}{%
    \iffieldundef{usera}{}{\setunit{\cv@linksep}\printfield[cv:paperpage]{usera}}%
  }{\setunit{\cv@linksep}\printfield[cv:paperpage]{url}}%
}
\newbibmacro*{cv:paperlink}{%
  \cv@ifpublished{%
    \iffieldundef{doi}{\usebibmacro{cv:paperpage}}%
      {\setunit{\cv@linksep}\printfield[cv:doi]{doi}}%
  }{%
    \ifboolexpr{not test {\iffieldundef{eprint}} and
      (test {\iffieldequalstr{eprinttype}{arxiv}} or
       test {\iffieldequalstr{eprinttype}{arXiv}})}%
      {\setunit{\cv@linksep}\printfield[cv:arxiv]{eprint}}%
      {\usebibmacro{cv:paperpage}}%
  }%
}
\renewbibmacro*{finentry}{%
  \usebibmacro{cv:paperlink}%
  \iffieldundef{userb}{}{\setunit{\cv@linksep}\printfield{userb}}%
  \iffieldundef{userc}{}{\setunit{\cv@linksep}\printfield{userc}}%
  \finentry
}
