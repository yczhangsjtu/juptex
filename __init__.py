from juptex.document import DocumentManager as Document
from juptex.text import TextManager
from juptex.notebook import isnotebook, register_cell_magic


global the_text_manager
the_text_manager = TextManager()


if isnotebook():
  @register_cell_magic
  def inline_math(line, content):
    return the_text_manager._math_manager.view(content, '$')
