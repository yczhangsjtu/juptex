import os
from numbers_parser import Document, TextCell
from juptex.config import *
from juptex.text import TextManager
from juptex.utils import *


class Column(object):

  """A column in a table"""

  def __init__(self, name):
    """Initialize the column

    :name: the identifier of the column

    """
    self._name = name
    self._left_border = 0
    self._right_border = 0
    self._align = "center"

  def set_left_border(self, border):
    self._left_border = border

  def set_right_border(self, border):
    self._right_border = border

  def set_align(self, align):
    self._align = align


class Row(object):

  """A row in a table."""

  def __init__(self, size):
    """Initialized to be empty."""
    self._cells = [Cell() for i in range(size)]
    self._top_border = 0
    self._bottom_border = 0
    for cell in self._cells:
      cell._row = self

  def set_header(self):
    self._bottom_border = 1
    for cell in self._cells:
      cell.set_bold()

  def set_cell(self, i, content):
    self._cells[i].set_content(content)

  def set_top_border(self, border):
    self._top_border = border

  def set_bottom_border(self, border):
    self._bottom_border = border

  def dump(self):
    return " & ".join(self.get_content_list())

  def get_content_list(self):
    ret = []
    to_skip = 0
    for i in range(len(self._cells)):
      if to_skip > 0:
        to_skip -= 1
        continue
      ret.append(self._cells[i].dump())
      to_skip += self._cells[i]._col_span - 1
    return ret


class Cell(object):

  """A cell in a row."""

  def __init__(self, content=None):
    """Initialize with a sentence or None

    :content: A sentence or None

    """
    self._content = content
    self._row_span = 1
    self._col_span = 1
    self._vertical_align = "center"
    self._horizontal_align = "default"
    self._bold = False
    self._left_border = 0
    self._right_border = 0

  def set_content(self, content=None):
    self._content = content

  def set_bold(self):
    self._bold = True

  def set_left_border(self, border):
    self._left_border = border

  def set_right_border(self, border):
    self._right_border = border

  def row_span(self, count):
    self._row_span = count

  def row_span_to_end(self):
    self._row_span = len(self._row._table._rows) - self._row._index

  def col_span(self, count):
    self._col_span = count

  def col_span_to_end(self):
    self._col_span = self._column._table.n_columns() - self._column._index

  def set_horizontal_align(self, align):
    self._horizontal_align = align

  def set_vertical_align(self, align):
    self._vertical_align = align

  def dump(self):
    if self._content is None:
      return ""
    content = self._content
    if len(content) == 0:
      return ""
    if self._bold:
      content = r"\textbf{%s}" % content
    if self._col_span > 1:
      if self._horizontal_align == "center":
        align = "c"
      elif self._horizontal_align == "left":
        align = "l"
      elif self._horizontal_align == "right":
        align = "r"
      elif self._horizontal_align == "default":
        align = "l"
      else:
        raise Exception(
            f"Unsupported horizontal align {self._horizontal_align}")
      if self._left_border > 0:
        align = "|" + align
      if self._right_border > 0:
        align = align + "|"
      content = r"\multicolumn{%d}{%s}{%s}" % (self._col_span, align, content)
    if self._row_span > 1:
      content = r"\multirow{%d}{*}{%s}" % (self._row_span, content)
    return content


class Cline(object):
  """A line in the table that spans only some columns"""

  def __init__(self, start, end):
    """Initialize with the start and end columns

    :start: the start column
    :end: the end column

    """
    self._start = start
    self._end = end

  def dump(self):
    return r"\cline{%d-%d}" % (self._start, self._end)


class Table(object):

  """A table in the paper."""

  def __init__(self, name):
    """Initialize an empty table

    :name: The identifier for this table

    """
    self._name = name
    self.clear()

  def clear(self):
    self._columns = []
    self._rows = []
    self._caption = None
    self._left_border = 0
    self._right_border = 0
    self._top_border = 2
    self._bottom_border = 2
    self._cell_map = {}

  def no_column(self):
    return len(self._columns) == 0

  def n_columns(self):
    return len(self._columns)

  def set_columns(self, column_names):
    self._columns = [Column(name) for name in column_names]
    for i in range(len(self._columns)):
      self._columns[i]._index = i
      self._columns[i]._table = self

  def add_row(self, points, sentences):
    assert not self.is_empty()
    assert self.n_columns() == len(sentences)
    row = Row(len(sentences))
    row._index = len(self._rows)
    row._table = self
    for i in range(len(sentences)):
      row.set_cell(i, sentences[i])
      if sentences[i] is not None:
        self._cell_map[points[i]] = row._cells[i]
      row._cells[i]._column = self._columns[i]
    self._rows.append(row)

  def is_empty(self):
    return self._columns is None or self._rows is None

  def caption(self, title):
    self._caption = self._paper.find_sentence(title)

  def label(self):
    return "tab:" + to_label(self._name)

  def ref(self):
    return r"Table~\ref{%s}" % self.label()

  def get_column(self, name):
    for column in self._columns:
      if column._name == name:
        return column
    raise Exception(f"Cannot find column with name {name}")

  def get_row(self, index):
    return self._rows[index]

  def find_cell(self, point):
    return self._cell_map[point]

  def find_row(self, point):
    return self.find_cell(point)._row

  def render_vertical_border(self, border):
    if border == 0:
      return ""
    if border == 1:
      return "|"
    raise Exception(f"Does not support border number {border}")

  def render_horizontal_border(self, border):
    if border == 0:
      return ""
    if border == 1:
      return "\\hline"
    if border == 2:
      return "\\hline\n\n\\hline"
    if isinstance(border, Cline):
      return border.dump()
    raise Exception(f"Does not support border number {border}")

  def dump_aligns(self):
    ret = []
    left_border = max(self._left_border, self._columns[0]._left_border)
    ret.append(self.render_vertical_border(left_border))
    for i in range(len(self._columns)):
      column = self._columns[i]
      if column._align == "left":
        ret.append("l")
      elif column._align == "center":
        ret.append("c")
      elif column._align == "right":
        ret.append("r")
      elif column._align.endswith("cm"):
        ret.append(f"p{{{column._align}}}")
      else:
        raise Exception(f"Unsupported horizontal alignment {column._align}")
      if i == len(self._columns) - 1:
        right_border = max(column._right_border, self._right_border)
      else:
        right_border = max(column._right_border,
                           self._columns[i+1]._left_border)
      ret.append(self.render_vertical_border(right_border))
    return "".join(ret)

  def dump_tabular_body(self):
    ret = []
    top_border = max(self._top_border, self._rows[0]._top_border)
    ret.append(self.render_horizontal_border(top_border))
    for i in range(len(self._rows)):
      row = self._rows[i]
      ret.append(row.dump())
      if i == len(self._rows) - 1:
        if isinstance(row._bottom_border, Cline):
          bottom_border = row._bottom_border
        elif isinstance(self._bottom_border, Cline):
          bottom_border = self._bottom_border
        else:
          bottom_border = max(row._bottom_border, self._bottom_border)
        if bottom_border > 0:
          ret[-1] += "\\\\ "
          ret[-1] += self.render_horizontal_border(bottom_border)
      else:
        if isinstance(row._bottom_border, Cline):
          bottom_border = row._bottom_border
        elif isinstance(self._rows[i+1]._top_border, Cline):
          bottom_border = self._rows[i+1]._top_border
        else:
          bottom_border = max(row._bottom_border, self._rows[i+1]._top_border)
        ret[-1] += "\\\\"
        if bottom_border != 0:
          ret[-1] += " " + self.render_horizontal_border(bottom_border)
    return "\n".join(ret)

  def dump_tabular(self):
    return r"""\begin{tabular}{%s}
%s
\end{tabular}""" % (self.dump_aligns(), self.dump_tabular_body())

  def dump(self):
    assert not self.is_empty()
    env_name = "table*" if self._cross_columns else "table"
    return r"""\begin{%s}[ht]
\caption{%s}
\label{%s}
%s
\end{%s}""" % (env_name,
               self._caption.dump(),
               self.label(),
               self.dump_tabular(),
               env_name)


class TableManager(object):
  def __init__(self, text_manager=None, math_manager=None):
    self._text_manager = (text_manager if text_manager is not None
                          else TextManager(math_manager))
    self._locals = self._text_manager._locals
    self._cross_columns = False
    self.define("mm", self._text_manager._math_manager)

  def get(self, key):
    return self._locals[key]

  def set_local_variables(self, variables):
    for key, value in variables.items():
      self._locals[key] = value

  def define(self, key, value):
    self._locals[key] = value

  def common_definitions_for_crypto(self):
    self._text_manager.common_definitions_for_crypto()

  def add_meta(self, line):
    self._text_manager.add_meta(line)

  def define_latex(self, command, content):
    self._text_manager.define_latex(command, content)

  def render_meta(self):
    return self._text_manager.render_meta()

  def wide(self):
    self._cross_columns = True

  def read(self, name):
    if name.endswith(".numbers"):
      tabulars = []
      doc = Document(name)
      sheets = doc.sheets
      tables = sheets[0].tables
      self.name = name
      for table in tables:
        latex_table = Table(name)
        rows = tables[0].rows()
        column_ids = rows[0]
        data = rows[1:]
        m, n = len(data), len(data[0])
        latex_table.set_columns([item.value.strip() for item in column_ids])
        for i in range(m):
          sentences = []
          for j in range(n):
            if isinstance(data[i][j], TextCell):
              sentences.append(self._text_manager(data[i][j].value.strip()))
            else:
              sentences.append(None)
          latex_table.add_row(
              [item.value.strip() if item.value is not None
               else None
               for item in data[i]],
              sentences)
          for j in range(n):
            if isinstance(data[i][j], TextCell):
              latex_table.get_row(i)._cells[j].row_span(data[i][j].size[0])
              latex_table.get_row(i)._cells[j].col_span(data[i][j].size[1])
        tabulars.append(latex_table)
      return tabulars
    else:
      raise ValueError("Can only support Numbers file now.")

  def __call__(self, tabulars, title, label):
    env_name = "table*" if self._cross_columns else "table"
    return r"""\begin{%s}[ht]
\caption{%s}
\label{%s}
%s
\end{%s}""" % (env_name,
               self._text_manager(title),
               label,
               "\n\n".join([tab.dump_tabular() for tab in tabulars]),
               env_name)
