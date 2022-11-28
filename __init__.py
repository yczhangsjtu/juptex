from juptex.document import DocumentManager as Document
from juptex.text import TextManager
from juptex.notebook import isnotebook, register_cell_magic
from juptex.preview import genpng
from juptex.utils import split_two_by_empty_line


global the_text_manager
the_text_manager = TextManager()


if isnotebook():
  @register_cell_magic
  def inline_math(line, content):
    return the_text_manager._math_manager.view(content, '$')

  @register_cell_magic
  def tikz(line, content):
    return genpng("\\begin{tikzpicture}\n" + content + "\n\\end{tikzpicture}")

  @register_cell_magic
  def tikzfig(line, content):
    lines = content.split("\n")
    title, content = split_two_by_empty_line(lines)
    return genpng("\\begin{figure}\\centering\\begin{tikzpicture}\n" +
                  "\n".join(content) + "\n\\end{tikzpicture}\n\\caption{" +
                  "\n".join(title) +
                  "}\n\\end{figure}")

  @register_cell_magic
  def tikzfigwide(line, content):
    lines = content.split("\n")
    title, content = split_two_by_empty_line(lines)
    return genpng("\\begin{figure*}\\centering\\begin{tikzpicture}\n" +
                  "\n".join(content) + "\n\\end{tikzpicture}\n\\caption{" +
                  "\n".join(title) +
                  "}\n\\end{figure*}")
