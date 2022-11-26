def isnotebook():
  try:
    shell = get_ipython().__class__.__name__
    if shell == 'ZMQInteractiveShell':
      return True   # Jupyter notebook or qtconsole
    elif shell == 'TerminalInteractiveShell':
      return False  # Terminal running IPython
    else:
      return False  # Other type (?)
  except NameError:
    return False      # Probably standard Python interpreter


if isnotebook():
  from IPython.display import Image
  from IPython.core.magic import register_cell_magic, register_line_magic
else:
  Image = None
  register_cell_magic = None
  register_line_magic = None
