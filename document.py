import os
import re
import json
from pybtex.database import parse_file, BibliographyData
from juptex.config import *
from juptex.matheq import *
from juptex.text import *
from juptex.table import *
from juptex.figure import *
from juptex.algorithm import *
from juptex.errors import *
from juptex.utils import *
from juptex.keywords import *
from juptex.author import *


class DocumentManager(object):
  def __init__(self, name, text_manager=None, math_manager=None):
    self._name = name
    self._text_manager = (text_manager if text_manager is not None
                          else TextManager(math_manager))
    self._locals = self._text_manager._locals
    self._authors = AuthorManager()
    self._keywords = Keywords()
    self._anonymous = False
    self._date = None
    self._title = ""
    self._meta = []
    self._outline_each_section = False
    self.define("mm", self._text_manager._math_manager)

  def anonymous(self):
    self._anonymous = True

  def outline_each_section(self):
    self._outline_each_section = True

  def set_title(self, title):
    self._title = title

  def set_date(self, date=""):
    self._date = date

  def add_meta(self, line):
    self._meta.append(line)

  def define_latex(self, command, content):
    if command in ["vec", "emph"]:
      name = "renewcommand"
    else:
      name = "newcommand"

    if "#" not in content:
      self._meta.append(r"\%s{\%s}{%s}" % (name, command, content))
      return
    nargs = 0
    for i in range(1, 10):
      if f"#{i}" in content:
        nargs = i
    if nargs == 0:
      self._meta.append(r"\%s{\%s}{%s}" % (name, command, content))
      return
    self._meta.append(r"\%s{\%s}[%d]{%s}" % (name, command, nargs, content))

  def get(self, key):
    return self._locals[key]

  def set_local_variables(self, variables):
    for key, value in variables.items():
      self._locals[key] = value

  def define(self, key, value):
    self._locals[key] = value

  def common_definitions_for_crypto(self):
    self._text_manager.common_definitions_for_crypto()

  def add_author(self, author):
    self._authors.add_author(author)

  def add_keyword(self, keyword):
    self._keywords.add_keyword(keyword)

  def __call__(self, notebook, template="lncs"):
    is_slide = template == "beamer"
    target_path = slide_path if is_slide else essay_path
    cells = get_cells(notebook)
    preprocessed_cells = self.preprocess_cells(cells)
    compiled_cells = self.compile_cells(preprocessed_cells)
    abstract, body, appendix = self.post_process(compiled_cells)
    self.copy_template(template)
    if len(abstract) > 0:
      with open(os.path.join(target_path, self._name, "abstract.tex"),
                "w") as f:
        f.write(abstract)
    if len(body) > 0:
      with open(os.path.join(target_path, self._name, "body.tex"), "w") as f:
        f.write(body)
    if len(abstract) > 0:
      with open(os.path.join(target_path, self._name, "appendix.tex"),
                "w") as f:
        f.write(r"\begin{appendix}")
        f.write(appendix)
        f.write(r"\end{appendix}")
    with open(os.path.join(target_path, self._name, "main.tex")) as f:
      content = f.read()
    content = content.replace("<author>", self._render_author(template))
    content = content.replace("<date>", self._render_date())
    content = content.replace("<keywords>", self._keywords.dump())
    content = content.replace("<title>", self._title)
    content = content.replace("<meta>", self._render_meta(is_slide))
    with open(os.path.join(target_path, self._name, "main.tex"), "w") as f:
      f.write(content)

  def _render_author(self, template):
    if template == "lncs":
      return self._authors.dump_lncs()
    if template == "acm":
      return self._authors.dump_acm()
    if template == "blog":
      return self._authors.dump_blog()
    raise ValueError(f"Unknown template: {template}")

  def _render_date(self):
    if self._date is None:
      return ""
    return r"\date{%s}" % self._date

  def _render_meta(self, is_slide):
    ret = "\n".join(self._meta)
    if self._outline_each_section:
      ret += r"""
\AtBeginSection[]
{
    \begin{frame}
        \frametitle{Outline}
        \tableofcontents[currentsection]
    \end{frame}
}
"""
    return ret

  def copy_template(self, template):
    is_slide = template == "beamer"
    target_path = slide_path if is_slide else essay_path
    script_path = Path(__file__).parent.absolute()
    if not os.path.isdir(os.path.join(essay_path, self._name)):
      os.mkdir(os.path.join(essay_path, self._name))
    os.system(f"cp {script_dir}/templates/{template}/* "
              f"'{os.path.join(target_path, self._name)}'")

  def preprocess_cells(self, cells):
    return cells

  def compile_cells(self, cells):
    return cells

  def post_process(self, cells):
    return abstract, body, appendix
