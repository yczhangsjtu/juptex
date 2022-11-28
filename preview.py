import os
from juptex.notebook import isnotebook, Image
from juptex.config import *


def genpdf(content, meta=None, clean=False, postfix=""):
  content = enclose_with_template(content, meta)
  has_reference = need_reference(content)
  if not os.path.isdir("./view"):
    os.mkdir("view")
  if clean:
    ret = os.system(f"cd view && rm -rf view*")
    if ret != 0:
      print(f"Exit with error: {ret}")
      return False
  with open(f"./view/view{postfix}.tex", "w") as f:
    f.write(content)
  if has_reference:
    ret = os.system(f"cp {bib_path} ./view")
    if ret != 0:
      print(f"Exit with error: {ret}")
      return False
    ret = os.system("cd view && latexmk -pdf -halt-on-error -silent "
                    "> /dev/null 2> error.log")
  else:
    ret = os.system(f"cd view && pdflatex view{postfix}.tex "
                    "-halt-on-error -silent "
                    "> /dev/null 2> error.log")
  if ret != 0:
    print(f"Exit with error: {ret}")
    return False

  return True


def need_reference(content):
  return content.find("\\cite{") >= 0


def enclose_with_template(content, meta=None):
  has_reference = need_reference(content)
  no_standalone = has_reference or content.find("\\begin{multline") >= 0
  no_standalone = no_standalone or content.find("\\begin{figure*") >= 0
  no_standalone = no_standalone or content.find("\\begin{algorithm") >= 0
  wide = content.find("\\begin{figure*") >= 0
  has_tikz = content.find("\\begin{tikzpicture}") >= 0
  has_tikz = has_tikz or content.find("\\tikz") >= 0
  if no_standalone:
    header = general_header
  elif has_tikz:
    header = standalone_tikz_header
  else:
    header = standalone_header
  temp = template.replace("<header>", header)
  temp = temp.replace("<geometry>", wide_page if wide else "")
  temp = temp.replace("<tikz_code>", tikz_code if has_tikz else "")
  temp = temp.replace("<bibliography>", bibliography if has_reference else "")
  temp = temp.replace("<meta>", meta if meta is not None else "")
  return temp % content


def genpng(content, meta=None, crop=True):
  if not genpdf(content, meta):
    raise Exception("Failed to generate pdf")

  if crop:
    ret = os.system("pdfcrop ./view/view.pdf ./view/view-crop.pdf "
                    "1> /dev/null 2> /dev/null")
    if ret != 0:
      raise Exception(f"pdfcrop exit with error: {ret}")

    ret = os.system(
        "convert -density 600 ./view/view-crop.pdf "
        "./view/view.png 2> /dev/null")
    if ret != 0:
      raise Exception(f"Convert exit with error: {ret}")
  else:
    ret = os.system(
        "convert -density 600 ./view/view.pdf ./view/view.png 2> /dev/null")
    if ret != 0:
      raise Exception(f"Convert exit with error: {ret}")

  if isnotebook():
    return Image("./view/view.png")
  else:
    os.system("open ./view/view.png")


tikz_code = r"""
\usepackage{tikz}
\usetikzlibrary{positioning}
\usetikzlibrary{shapes}
\usetikzlibrary{shapes.geometric}
\usetikzlibrary{decorations.pathreplacing}
\usetikzlibrary{decorations.text}
"""


bibliography = r"""
\bibliographystyle{alpha}
\bibliography{reference}
"""


standalone_header = r"\documentclass[crop,tikz]{standalone}"


standalone_tikz_header = r"\documentclass[crop,tikz]{standalone}"


general_header = r"\documentclass{article}"


wide_page = r"""
\usepackage{geometry}
\geometry{
 a4paper,
 left=10mm,
 right=10mm,
}
"""


template = r"""<header>
<geometry>
\usepackage{lmodern}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{textcomp}
\usepackage{ulem}
\usepackage{bbm}
\usepackage{xcolor}
\usepackage{CJKutf8}
\usepackage{multirow}
\usepackage{multicol}
\usepackage{algorithm}
\usepackage{algpseudocode}
\newtheorem{theorem}{Theorem}[section]
\newtheorem{corollary}{Corollary}[theorem]
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{remark}[theorem]{Remark}
\definecolor{olive}{rgb}{0.3, 0.4, .1}
\definecolor{fore}{RGB}{249,242,215}
\definecolor{back}{RGB}{51,51,51}
\definecolor{title}{RGB}{255,0,90}
\definecolor{dgreen}{rgb}{0.,0.6,0.}
\definecolor{gold}{rgb}{1.,0.84,0.}
\definecolor{JungleGreen}{cmyk}{0.99,0,0.52,0}
\definecolor{BlueGreen}{cmyk}{0.85,0,0.33,0}
\definecolor{RawSienna}{cmyk}{0,0.72,1,0.45}
\definecolor{Magenta}{cmyk}{0,1,0,0}
<tikz_code>

\newcommand{\blue}[1]{\textcolor{blue}{#1}}
\newcommand{\green}[1]{\textcolor{green}{#1}}
\newcommand{\dgreen}[1]{\textcolor{dgreen}{#1}}
\newcommand{\orange}[1]{\textcolor{orange}{#1}}
\newcommand{\red}[1]{\textcolor{red}{#1}}
\newcommand{\purple}[1]{\textcolor{purple}{#1}}
\newcommand{\olive}[1]{\textcolor{olive}{#1}}
\pagestyle{empty}
<meta>
\begin{document}
%s
\end{document}
<bibliography>
"""
