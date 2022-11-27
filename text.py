from juptex.config import *
from juptex.errors import *
from juptex.matheq import MathManager


class TextManager(object):
  def __init__(self, math_manager=None):
    self._bib_path = bib_path
    self._math_manager = (math_manager if math_manager is not None
                          else MathManager())
    self._locals = self._math_manager._locals
    self.define("mm", self._math_manager)

  def get(self, key):
    return self._locals[key]

  def set_local_variables(self, variables):
    for key, value in variables.items():
      self._locals[key] = value

  def define(self, key, value):
    self._locals[key] = value

  def common_definitions_for_crypto(self):
    self._math_manager.common_definitions_for_crypto()

  def compile_math(self, code):
    try:
      return self._math_manager(code)
    except MathEquationError as e:
      raise MathEquationError(
          f"Error in compiling math code:\n{code}\nError: {e}")

  def __call__(self, content):
    content = content.replace(space_placeholder, " ")

    mode = "normal"
    buffer = []
    double_quote_is_open = False

    """
    Put the passed variables into the local variables
    """
    if self._locals is not None:
      for key, value in self._locals.items():
        locals()[key] = value

    while len(content) > 0:
      if mode == "normal":
        blockmath_index = content.find(blockmath_start_mark)
        math_index = content.find(math_start_mark)
        bold_index = content.find(bold_start_mark)
        emph_index = content.find(emph_start_mark)
        cite_index = content.find(cite_start_mark)
        pre_index = content.find(pre_start_mark)
        double_quote_index = content.find('"')
        python_index = content.find(python_start_mark)

        indices = [blockmath_index, math_index, bold_index, emph_index,
                   cite_index, pre_index, double_quote_index, python_index]
        modes = ["blockmath", "math", "bold", "emph", "cite",
                 "pre", "dquote", "python"]
        start_mark_lengths = [
            len(blockmath_start_mark), len(math_start_mark),
            len(bold_start_mark), len(emph_start_mark),
            len(cite_start_mark), len(pre_start_mark),
            len('"'), len(python_start_mark)]

        valid_indices = [(index, i)
                         for i, index in enumerate(indices)
                         if index != -1]
        if len(valid_indices) == 0:
          buffer.append(content)
          break

        index, i = min(valid_indices)
        buffer.append(content[:index])
        content = content[index+start_mark_lengths[i]:]
        mode = modes[i]
      elif mode == "python":
        index = content.find(python_end_mark)
        if index == -1:
          raise Exception(f"Failed to find python end mark "
                          f"when processing {content}")
        buffer.append(str(eval(content[:index], globals(), locals())))
        content = content[index+len(python_end_mark):]
        mode = "normal"
      elif mode == "blockmath":
        index = content.find(blockmath_end_mark)
        if index == -1:
          raise Exception(f"Failed to find block math end mark "
                          f"when processing {content}")
        math_content = content[:index]
        content = content[index+len(blockmath_end_mark):]
        buffer.append(r"\[%s\]" % self.compile_math(math_content))
        mode = "normal"
      elif mode == "math":
        index = content.find(math_end_mark)
        if index == -1:
          raise Exception(f"Failed to find math end mark "
                          f"when processing {content}")
        math_content = content[:index]
        content = content[index+len(math_end_mark):]
        buffer.append("$%s$" % self.compile_math(math_content))
        mode = "normal"
      elif mode == "bold":
        index = content.find(bold_end_mark)
        if index == -1:
          raise Exception(f"Failed to find bold end mark "
                          f"when processing {content}")
        buffer.append("\\textbf{%s}" % content[:index])
        content = content[index+len(bold_end_mark):]
        mode = "normal"
      elif mode == "emph":
        index = content.find(emph_end_mark)
        if index == -1:
          raise Exception(f"Failed to find emph end mark "
                          f"when processing {content}")
        buffer.append("\\emph{%s}" % content[:index])
        content = content[index+len(emph_end_mark):]
        mode = "normal"
      elif mode == "cite":
        index = content.find(cite_end_mark)
        if index == -1:
          raise Exception(f"Failed to find cite end mark "
                          f"when processing {content}")
        buffer.append("\\cite{%s}" % content[:index])
        content = content[index+len(cite_end_mark):]
        mode = "normal"
      elif mode == "pre":
        index = content.find(pre_end_mark)
        if index == -1:
          raise Exception(f"Failed to find pre end mark "
                          f"when processing {content}")
        buffer.append(content[:index])
        content = content[index+len(pre_end_mark):]
        mode = "normal"
      elif mode == "dquote":
        if double_quote_is_open:
          buffer.append("''")
        else:
          buffer.append("``")
        double_quote_is_open = not double_quote_is_open
        mode = "normal"
      else:
        assert False
    ret = "".join(buffer)
    ret = ret.replace(" \\cite{", "~\\cite{")
    return ret
