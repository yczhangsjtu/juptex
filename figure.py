import shutil
import os
from juptex.text import TextManager


class FigureManager(object):
  def __init__(self, text_manager=None, math_manager=None, image_path=None):
    self._text_manager = (text_manager if text_manager is not None
                          else TextManager(math_manager))
    self._locals = self._text_manager._locals
    self._image_path = image_path if image_path is not None else "./images"
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

  def __call__(self, path_to_figure, title, label, wide=False):
    if not os.path.exists(self._image_path):
      os.mkdir(self._image_path)
    if not os.path.isdir(self._image_path):
      raise IOError(f"{self._image_path} is not a directory")
    shutil.copy(path_to_figure, "./images")
    env_name = "figure*" if wide else "figure"
    return r"""\begin{%s}[ht]
  \includegraphics[width=\textwidth]{%s}
  \caption{%s}\label{%s}
\end{%s}""" % (env_name,
               os.path.join("images", os.path.basename(path_to_figure)),
               self._text_manager(title), label,
               env_name)
