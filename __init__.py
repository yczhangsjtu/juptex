import json
import os
import tkinter as tk
from juptex.document import DocumentManager as Document
from juptex.text import TextManager
from juptex.algorithm import AlgorithmManager
from juptex.notebook import isnotebook, register_cell_magic, \
    register_line_magic
from juptex.preview import genpng
from juptex.utils import split_two_by_empty_line
from juptex.author import Author, Institute


global the_text_manager
the_text_manager = TextManager()


if isnotebook():
  @register_cell_magic
  def inline_math(line, content):
    return the_text_manager._math_manager.view(content, '$')

  @register_cell_magic
  def block_math(line, content):
    return the_text_manager._math_manager.view(content, line.strip())

  @register_cell_magic
  def tikz(line, content):
    return genpng("\\begin{tikzpicture}\n" + content + "\n\\end{tikzpicture}",
                  the_text_manager.render_meta())

  @register_cell_magic
  def tikzfig(line, content):
    lines = content.split("\n")
    title, content = split_two_by_empty_line(lines)
    return genpng("\\begin{figure}\\centering\\begin{tikzpicture}\n" +
                  "\n".join(content) + "\n\\end{tikzpicture}\n\\caption{" +
                  "\n".join(title) +
                  "}\n\\end{figure}",
                  the_text_manager.render_meta())

  @register_cell_magic
  def tikzfigwide(line, content):
    lines = content.split("\n")
    title, content = split_two_by_empty_line(lines)
    return genpng("\\begin{figure*}\\centering\\begin{tikzpicture}\n" +
                  "\n".join(content) + "\n\\end{tikzpicture}\n\\caption{" +
                  "\n".join(title) +
                  "}\n\\end{figure*}",
                  the_text_manager.render_meta())

  @register_cell_magic
  def algorithm(line, content):
    algorithm = AlgorithmManager(text_manager=the_text_manager)
    return algorithm.view(content, line)

  @register_line_magic
  def draw(line):
    import english2tikz
    name = line.strip()
    di = english2tikz.DescribeIt()
    with open("data/" + name + ".json") as f:
      content = json.load(f)
    di._picture = content["picture"]
    content = di.render()
    return genpng(content, the_text_manager.render_meta())

  @register_line_magic
  def drawgui(line):
    name = line.strip()
    filename = "data/" + name + ".json"
    if not os.path.exists(filename):
      with open(filename, "w") as f:
        f.write("{}")
    with open(filename) as f:
      content = f.read()
    launch_draw_gui(content, filename)

  @register_cell_magic
  def drawfig(line, content):
    import english2tikz
    title = content.strip()
    name = line.strip()
    di = english2tikz.DescribeIt()
    with open("data/" + name + ".json") as f:
      content = json.load(f)
    di._picture = content["picture"]
    content = di.render()
    return genpng("\\begin{figure}\\centering\n" +
                  content + "\n\\caption{" + title +
                  "}\n\\end{figure}",
                  the_text_manager.render_meta())

  @register_cell_magic
  def drawwide(line, content):
    import english2tikz
    title = content.strip()
    name = line.strip()
    di = english2tikz.DescribeIt()
    with open("data/" + name + ".json") as f:
      content = json.load(f)
    di._picture = content["picture"]
    content = di.render()
    return genpng("\\begin{figure*}\\centering\n" +
                  content + "\n\\caption{" + title +
                  "}\n\\end{figure*}",
                  the_text_manager.render_meta())

  @register_cell_magic
  def drawfiggui(line, content):
    drawgui(line)


def launch_draw_gui(content, filename=None):
  import english2tikz
  screen_width, screen_height = 1200, 750
  data = json.loads(content)
  root = tk.Tk()
  canvas = tk.Canvas(root, bg="white", width=screen_width,
                     height=screen_height)
  canvas.pack()

  editor = english2tikz.Editor(root, canvas, screen_width, screen_height)
  editor.load(data)
  editor.filename = filename

  root.title("Vim Draw")
  root.minsize(screen_width, screen_height)
  root.configure(bg="white")
  root.mainloop()
