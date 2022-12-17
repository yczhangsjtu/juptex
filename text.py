from juptex.config import *
from juptex.errors import *
from juptex.matheq import MathManager
from juptex.utils import *


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

  def add_meta(self, line):
    self._math_manager.add_meta(line)

  def define_latex(self, command, content):
    self._math_manager.define_latex(command, content)

  def render_meta(self):
    return self._math_manager.render_meta()

  def __call__(self, content):
    transpilers = [
      BlockMathTranspiler(self._math_manager),
      MathTranspiler(self._math_manager),
      BoldTranspiler(),
      EmphTranspiler(),
      UnderlineTranspiler(),
      CiteTranspiler(),
      RawTranspiler(),
      PreTranspiler(),
      DquoteTranspiler(),
      PythonTranspiler(self._locals),
    ]
    content = content.replace(space_placeholder, " ")
    buffer, past = [], ""
    while len(content) > 0:
      transpiler, start, end = None, None, None
      for t in transpilers:
        s, e = t.find(content)
        if s is not None and (start is None or s < start):
          transpiler, start, end = t, s, e
      if transpiler is None:
        buffer.append(content)
        content = ""
        break
      if end is None:
        info = (past+content)[max(start+len(past)-20,0):
                              min(start+20,len(content)+len(past))]
        raise ValueError(f"Unended {transpiler}: ... '{info}' ...")
      buffer.append(content[:start])
      buffer.append(transpiler.transpile(transpiler.trim(content[start:end])))
      past += content[:end]
      content = content[end:]
      
    ret = "".join(buffer)
    ret = ret.replace(" \\cite{", "~\\cite{")
    return ret
  

class Transpiler(object):
  def __init__(self,
               start_mark=None,
               end_mark=None,
               prefix=None,
               suffix=None):
    self._start_mark = start_mark
    self._end_mark = end_mark
    self._prefix = prefix
    self._suffix = suffix
    
  def find(self, s):
    start = s.find(self._start_mark)
    if start < 0:
      return None, None
    end = s.find(self._end_mark, start + len(self._start_mark))
    if end < 0:
      return start, None
    return start, end + len(self._end_mark)
  
  def trim(self, s):
    return s[len(self._start_mark):-len(self._end_mark)]
  
  def transpile(self, s):
    return self._prefix + s + self._suffix
  
  def __str__(self):
    return self._start_mark


class MathTranspiler(Transpiler):
  def __init__(self, math_manager):
    super().__init__(math_start_mark, math_end_mark)
    self._math_manager = math_manager
  
  def transpile(self, s):
    try:
      return f"${self._math_manager(s)}$"
    except MathEquationError as e:
      raise MathEquationError(
          f"Error in compiling math code:\n{s}\nError: {e}")


class BlockMathTranspiler(Transpiler):
  def __init__(self, math_manager):
    super().__init__(blockmath_start_mark, blockmath_end_mark)
    self._math_manager = math_manager
  
  def transpile(self, s):
    try:
      return f"\[{self._math_manager(s)}\]"
    except MathEquationError as e:
      raise MathEquationError(
          f"Error in compiling math code:\n{s}\nError: {e}")

class BoldTranspiler(Transpiler):
  def __init__(self):
    super().__init__(bold_start_mark,
                     bold_end_mark,
                     r"\textbf{",
                     r"}")
    

class EmphTranspiler(Transpiler):
  def __init__(self):
    super().__init__(emph_start_mark,
                     emph_end_mark,
                     r"\emph{",
                     r"}")
    

class UnderlineTranspiler(Transpiler):
  def __init__(self):
    super().__init__(underline_start_mark,
                     underline_end_mark,
                     r"\underline{",
                     r"}")
    

class CiteTranspiler(Transpiler):
  def __init__(self):
    super().__init__(cite_start_mark,
                     cite_end_mark,
                     r"\cite{",
                     r"}")
    

class RawTranspiler(Transpiler):
  def __init__(self):
    super().__init__(raw_start_mark,
                     raw_end_mark,
                     r"", r"")
    

class PreTranspiler(Transpiler):
  def __init__(self):
    super().__init__(pre_start_mark,
                     pre_end_mark,
                     r"", r"")
  
  def transpile(self, s):
    deliminator = find_special_char_not_in(s)
    if deliminator is None:
      raise ValueError(f"{s} contains all possible deliminators")
    return r"\verb" + deliminator + s + deliminator
    

class DquoteTranspiler(Transpiler):
  def __init__(self):
    self._open = False
  
  def find(self, s):
    index = find_first_unescaped_quote(s)
    if index < 0:
      return None, None
    return index, index + 1
  
  def trim(self, s):
    return s
  
  def transpile(self, s):
    if not self._open:
      self._open = True
      return '``'
    self._open = False
    return "''"
  
  def __str__(self):
    return "double quote"
  

class PythonTranspiler(Transpiler):
  def __init__(self, vars):
    super().__init__(python_start_mark, python_end_mark)
    self._vars = vars
  
  def transpile(self, s):
    if self._vars is not None:
      for key, value in self._vars.items():
        locals()[key] = value
    return str(eval(s, globals(), locals()))
