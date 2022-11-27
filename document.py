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
from juptex.paragraph import *
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
    processed_cells = self.process_cells(preprocessed_cells, is_slide)
    compiled_cells = self.compile_cells(processed_cells, is_slide)
    abstract, body, appendix = self.post_process(compiled_cells, is_slide)
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
    if template == "beamer":
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
    ret = []
    for type_, content in cells:
      if type_ == "markdown":
        cell = self._preprocess_markdown(content)
        if cell is not None:
          if cell.get("type") == "end":
            return ret
          ret.append(cell)
      elif type_ == "code":
        cell = self._preprocess_code(content)
        if cell is not None:
          ret.append(cell)
      else:
        raise ValueError(f"Unexpected type {type_}")
    return ret

  def _preprocess_markdown(self, content):
    if len(content.strip()) == 0:
      return {"type": "empty"}
    if self.title is not None and content == "# The End":
      return {"type": "end"}
    lines = content.split("\n")
    start_line = lines[0].strip()
    if len(lines) == 1:
      res = self._preprocess_single_line(start_line)
      if res is not None:
        return res

    match = re.match(
        r"\*\*(Theorem|Lemma|Proof|Corollary|Remark|Definition)"
        r"( \(.+?\))?\*\*\.(.*)", start_line)
    if match:
      env_name = match.group(1)
      title = match.group(2)
      rest = match.group(3)
      if title is not None:
        title = title[2:-1]
      return self._preprocess_environment(lines[1:], env_name, title, rest)

    if start_line == "---":
      return {"type": "endframe"}

    if start_line == "---":
      if lines[1].startswith("#### "):
        title = lines[1][5:]
      else:
        title = None
      ret_lines = []
      for i in range(2, len(lines)):
        line, comments = extract_html_comment(lines[i])
        if "Ignore" in comments:
          continue
        if line.strip() == "" and lines[i].strip() != "":
          """
          An empty line caused by stripping the comments should be skipped
          so that the lines before and after this line are still treated as
          if they are in one paragraph.
          """
          continue
        ret_lines.append(line)
      return {
          "type": "slide",
          "lines": ret_lines,
          "title": title,
      }

    ret_lines = []
    for i in range(len(lines)):
      line, comments = extract_html_comment(lines[i])
      if "Ignore" in comments:
        continue
      if line.strip() == "" and lines[i].strip() != "":
        """
        An empty line caused by stripping the comments should be skipped
        so that the lines before and after this line are still treated as
        if they are in one paragraph.
        """
        continue
      ret_lines.append(line)
    return {
        "type": "text",
        "lines": ret_lines
    }

  def _preprocess_single_line(self, line):
    if line.startswith("# "):
      title = line[2:].strip()
      self.set_title(title)
      return {"type": "empty"}
    elif line.startswith("## ") or line.startswith("### "):
      return self._preprocess_section_title(line)
    elif line == "---":
      return {"type": "endslide"}
    else:
      return None

  def _preprocess_section_title(self, line):
    if line.startswith("## "):
      section_title = line[3:].strip()
      category = "section"
      prefix = "sec"
    elif line.startswith("### "):
      section_title = line[4:].strip()
      category = "subsection"
      prefix = "subsec"
    else:
      raise ValueError(f"Impossible line {line}")

    if section_title == "Abstract":
      return {"type": "abstract"}

    if section_title == "Appendix":
      return {"type": "appendix"}

    title, label = self._preprocess_title_with_comments(section_title, prefix)
    return {
        "type": category,
        "title": title,
        "label": label
    }

  def _preprocess_title_with_comments(self, title, prefix):
    title, comments = extract_html_comment(title)
    title = title.strip()
    if len(comments) > 0:
      label = comments[0]
    else:
      label = to_label(title)
    self.define(f"{prefix}_{to_word(label)}",
                r"Section~\ref{%s:%s}" % (prefix, label))
    return title, label

  def _preprocess_environment(self, lines, env_name, title, rest):
    if env_name == "Proof":
      label, prefix = None, None
    else:
      _, comments = extract_html_comment(rest)
      if len(comments) > 0:
        label = comments[0]
      elif title:
        label = to_label(title)
      else:
        raise ValueError("No label nor title is given.")
      prefix = {
          "Theorem": "thm",
          "Lemma": "lem",
          "Corollary": "col",
          "Remark": "rmk",
          "Definition": "def",
      }[env_name]
      self.define("%s_%s" % (prefix, to_word(label)),
                  r"%s~\ref{%s:%s}" % (env_name, prefix, label))

    ret_lines = []
    for i in range(len(lines)):
      line, comments = extract_html_comment(lines[i])
      if "Ignore" in comments:
        continue
      if line.strip() == "" and lines[i].strip() != "":
        """
        An empty line caused by stripping the comments should be skipped
        so that the lines before and after this line are still treated as
        if they are in one paragraph.
        """
        continue
      ret_lines.append(line)
    return {
        "type": env_name.lower(),
        "title": title,
        "label": label,
        "prefix": prefix,
        "lines": ret_lines
    }

  def _preprocess_code(self, content):
    if len(content.strip()) == 0:
      return {"type": "empty"}
    lines = content.split()
    start_line = lines[0].strip()
    if start_line.startswith("%%algorithm "):
      name = start_line[12:].strip()
      self.define("alg_" + to_word(name),
                  r"Algorithm~\ref{alg:" + to_label(name) + "}")
      return {
          "type": "algorithm",
          "content": "\n".join(lines[1:]),
      }
    if start_line.startswith('%drawfile ') or start_line.startswith(
            '%drawfilegui ') or start_line.startswith(
            '%%drawfig ') or start_line.startswith(
            '%%drawfiggui ') or start_line.startswith("%%drawfigwide "):
      filename = start_line[start_line.find(' ')+1:].strip()
      enclose_figure = start_line.startswith('%%drawfig')
      title = lines[1:] if enclose_figure else None
      if enclose_figure:
        self.define("fig_" + to_word(filename),
                    r"Figure~\ref{fig:" + to_label(filename) + "}")
      with open(f"data/{filename}.json") as f:
        content = f.read()
      return {
          "type": "draw",
          "content": content,
          "name": filename,
          "title": "\n".join(title),
          "wide": start_line.startswith("%%drawfigwide ")
      }
    if start_line.startswith('%drawslide ') or start_line.startswith(
            '%drawslidegui '):
      filename = start_line[start_line.find(' ')+1:].strip()
      title = filename[filename.find(' ')+1:]
      filename = filename[:filename.find(' ')]
      with open(f"data/{filename}.json") as f:
        content = f.read()
      return {
          "type": "drawslide",
          "content": content,
          "title": "\n".join(title)
      }
    if start_line.startswith('%%tikz '):
      name = start_line[start_line.find(' ')+1].strip()
      return {
          "type": "tikz",
          "content": "\n".join(lines[1:]),
          "name": name,
      }
    if start_line == '%%tikz':
      return {
          "type": "tikz",
          "content": "\n".join(lines[1:]),
      }
    if start_line.startswith('%%tikzfig ') or \
       start_line.startswith('%%tikzfigwide '):
      name = start_line[start_line.find(' ')+1].strip()
      self.define("fig_" + to_word(name),
                  r"Figure~\ref{fig:" + to_label(name) + "}")
      empty_line = lines.index("")
      if empty_line >= 0:
        title = "\n".join(lines[1:empty_line])
        content = "\n".join(lines[empty_line+1:])
      else:
        raise ValueError(f"Tikzfig ({name}) should have both title and code")
      return {
          "type": "tikz",
          "content": content,
          "name": name,
          "title": title,
          "wide": start_line.startswith("%%tikzfigwide")
      }
    if start_line.startswith('%%tikzslide '):
      title = start_line[start_line.find(' ')+1:].strip()
      return {
          "type": "tikzslide",
          "content": "\n".join(lines[1:]),
          "title": title,
      }
    if start_line == "%%inline_math":
      return {"type": "math", "env": "$", "content": "\n".join(lines[1:])}
    if start_line.startswith("%%block_math "):
      env_name = start_line[13:].strip()
      content = "\n".join(lines[1:])
      labels = find_all_labels(content)
      for label in labels:
        self.define(to_word(label), r"Equation~\ref{%s}" % label)
      return {
          "type": "math",
          "content": content,
          "env": env_name
      }
    if start_line.startswith("%%figure "):
      path = start_line[9:].strip()
      name = os.path.basename(os.path.splitext(path)[0])
      self.define("fig_" + to_word(name),
                  r"Figure~\ref{fig:%s}" % to_label(name))
      return {
          "type": "figure",
          "path": path,
          "name": name,
          "title": "\n".join(lines[1:]),
      }
    if start_line.startswith("%%widefigure "):
      path = start_line[13:].strip()
      name = os.path.basename(os.path.splitext(path)[0])
      self.define("fig_" + to_word(name),
                  r"Figure~\ref{fig:%s}" % to_label(name))
      return {
          "type": "figure",
          "path": path,
          "name": name,
          "wide": True,
          "title": "\n".join(lines[1:]),
      }
    if start_line.startswith("%%table "):
      path = start_line[8:].strip()
      name = os.path.basename(os.path.splitext(path)[0])
      self.define("tab_" + to_word(name),
                  r"Table~\ref{tab:%s}" % to_label(name))
      return {
          "type": "table",
          "path": path,
          "name": name,
          "title": "\n".join(lines[1:]),
      }
    if start_line.startswith("%%widetable "):
      path = start_line[12:].strip()
      name = os.path.basename(os.path.splitext(path)[0])
      self.define("tab_" + to_word(name),
                  r"Table~\ref{tab:%s}" % to_label(name))
      return {
          "type": "table",
          "path": path,
          "name": name,
          "wide": True,
          "title": "\n".join(lines[1:]),
      }
    return None

  def process_cells(self, cells, is_slide):
    ret = []
    """
    First pass:
    1. split text into paragraphs
    2. mark by slides
    2. mark by theorems
    """
    started_environment = None
    for cell in cells:
      if started_environment is not None:
        if cell.get("type") not in ["text", "math"]:
          ret.append({"type": "end_" + started_environment})
          started_environment = False
      if cell.get("type") == "text":
        lines = cell["lines"]
        paragraphs = split_by_empty_lines(lines)
        for paragraph in paragraphs:
          ret.append({
              "type": "paragraph",
              "content": paragraph,
          })
      elif cell.get("type") == "slide":
        lines = cell["lines"]
        paragraphs = split_by_empty_lines(lines)
        ret.append({"type": "startslide", "title": cell.get("title")})
        for paragraph in paragraphs:
          ret.append({
              "type": "paragraph",
              "content": paragraph,
          })
      elif cell.get("type") == "tikzslide" or (
              is_slide and cell.get("type") == "tikz"
              and cell.get("title") is not None):
        ret.append({"type": "startslide", "title": cell.get("title")})
        ret.append({"type": "tikz", "content": cell.get("content")})
        ret.append({"type": "endslide"})
      elif cell.get("type") == "drawslide" or (
              is_slide and cell.get("type") == "draw"
              and cell.get("title") is not None):
        ret.append({"type": "startslide", "title": cell.get("title")})
        ret.append({"type": "draw", "content": cell.get("content")})
        ret.append({"type": "endslide"})
      elif cell.get("type") in ["theorem", "lemma", "corollary",
                                "remark", "definition"]:
        ret.append({
            "type": "start_" + cell.get("type"),
            "title": cell.get("title"),
            "label": cell.get("label"),
            "prefix": cell.get("prefix"),
            "lines": cell.get("lines"),
        })
        started_environment = cell.get("type")
      else:
        ret.append(cell)
    """
    Second pass: filter out slide or non-slide contents
    """
    cells, ret = ret, []
    slide_started = False
    for cell in cells:
      if is_slide:
        if cell.get("type") in ["section", "subsection", "startslide"]:
          ret.append(cell)
          if cell.get("type") == "startslide":
            slide_started = False
        elif slide_started:
          ret.append(cell)
          if cell.get("type") == "endslide":
            slide_started = False
      else:
        if cell.get("type") == "endslide":
          slide_started = False
        elif cell.get("type") == "startslide":
          slide_started = True
        elif not slide_started:
          ret.append(cell)
    return ret

  def compile_cells(self, cells, is_slide):
    """
    Require at least two passes, because we must first compile
    the math equations, then connect them with the paragraphs.
    To achieve this without messing with the paragraph compilation,
    we insert the math equations into the paragraphs, replaced by
    codes. After compiling the paragraphs, the codes with be
    replaced back.
    """
    code_dictionary = {}
    code_count = 0

    def f(cell):
      return cell

    def g(new_cell, original_cell, next_cell):
      if new_cell.get("type") == "text" and next_cell.get("type") == "math":
        content = self._text_manager._math_manager(next_cell["content"])
        if next_cell["env"] == "$":
          content = f"${content}$"
        else:
          content = r"""\begin{%s}
  %s
\end{%s}""" % (next_cell["env"], content, next_cell["env"])
        code = f"mathequationcode{code_count}"
        code += 1
        code_dictionary[code] = content

        if original_cell.get("type") != "math" or original_cell["env"] == "$":
          if next_cell["env"] == "$":
            connector = " "
          else:
            connector = "\n"
        else:
          connector = "\n"

        return {
            "type": "text",
            "content": new_cell["content"] + f"{connector}{code}",
        }
      if original_cell.get("type") == "math":
        if next_cell.get("type") == "text":
          if original_cell["env"] == "$":
            connector = " "
          else:
            connector = "\n"
          return {
              "type": "text",
              "content": new_cell["content"] + connector + next_cell["content"]
          }
      return None

    cells = map_with_merge(cells, f, g)

    """
    Second pass: compilation
    """
    ret, cells = [], ret
    belong = "body"
    target_path = slide_path if is_slide else essay_path
    for cell in cells:
      if cell.get("type") == "section":
        belong = "body"
        ret.append({
            "belong": belong,
            "content": r"\section{%s}\label{sec:%s}" % (
                cell.get("title"),
                cell.get("label"),
            ),
        })
      elif cell.get("type") == "subsection":
        belong = "body"
        ret.append({
            "belong": belong,
            "content": r"\subsection{%s}\label{subsec:%s}" % (
                cell.get("title"),
                cell.get("label"),
            ),
        })
      elif cell.get("type") == "startslide":
        title = cell.get("title")
        if title is not None:
          content = r"\begin{frame}\frametitle{%s}" % title
        else:
          content = r"\begin{frame}"
        ret.append({
            "belong": belong,
            "content": content,
        })
      elif cell.get("type") == "endslide":
        ret.append({
            "belong": belong,
            "content": r"\end{frame}",
        })
      elif cell.get("type") == "abstract":
        belong = "abstract"
      elif cell.get("type") == "appendix":
        belong = "appendix"
      elif cell.get("type") == "paragraph":
        ret.append({
            "belong": belong,
            "content": ParagraphManager(self._text_manager)(
                cell.get("content"))
        })
      elif cell.get("type") == "tikz":
        title = cell.get("title")
        content = cell.get("content")
        env = "figure" if not cell.get("wide", False) else "figure*"
        if title is not None:
          content = r"""\begin{%s}
\begin{tikzpicture}
%s
\end{tikzpicture}
\caption{%s}\label{fig:%s}
\end{%s}""" % (env, content,
               self._text_manager(cell.get("title")),
               to_label(cell.get("name")), env)
        ret.append({
            "belong": belong,
            "content": content
        })
      elif cell.get("type") == "draw":
        title = cell.get("title")
        content = cell.get("content")
        import english2tikz
        di = english2tikz.DescribeIt()
        di._picture = content["picture"]
        if "width" in content and "height" in content:
          width, height = content["width"], content["height"]
          di._scale = min(1, 11/width, 8/height)
        content = di.render()
        env = "figure" if not cell.get("wide", False) else "figure*"
        if title is not None:
          content = r"""\begin{%s}
%s
\caption{%s}\label{fig:%s}
\end{%s}""" % (env, content,
               self._text_manager(cell.get("title")),
               to_label(cell.get("name")), env)
        ret.append({
            "belong": belong,
            "content": content
        })
      elif cell.get("type") == "figure":
        content = FigureManager(
            text_manager=self._text_manager,
            image_path=target_path)(
                cell.get("path"), title,
                "fig:" + to_label(cell.get("name")),
                cell.get("wide", False))
        ret.append({
            "belong": belong,
            "content": content
        })
      elif cell.get("type") == "table":
        tm = TableManager(
            text_manager=self._text_manager,
            image_path=target_path)
        tabulars = tm.read(cell.get("path"))
        tabulars[0].get_row(0).set_header()
        content = tm(tabulars, title,
                     "tab:" + to_label(cell.get("name")),
                     cell.get("wide", False))
        ret.append({
            "belong": belong,
            "content": content
        })
      else:
        ret.append(cell)

    """
    Finally, set the codes back.
    """
    for cell in cells:
      for code, content in code_dictionary.items():
        cell["content"] = cell["content"].replace(code, content)

    return ret

  def post_process(self, cells, is_slide):
    abstract, body, appendix = [], [], []
    for cell in cells:
      if cell.get("belong") == "abstract":
        abstract.append(cell.get("content"))
      elif cell.get("belong") == "body":
        body.append(cell.get("content"))
      elif cell.get("belong") == "appendix":
        appendix.append(cell.get("content"))
      else:
        raise ValueError(f"Unknown belong {cell.get('belong')}")
    return "\n\n".join(abstract), "\n\n".join(body), "\n\n".join(appendix)
