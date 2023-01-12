import string
import re
from juptex.config import *
from juptex.errors import *
from juptex.notebook import *
from juptex.preview import *
from juptex.utils import *


greek_letters = [
    "alpha", "beta", "gamma", "delta", "epsilon",
    "zeta", "eta", "theta", "iota", "kappa",
    "lambda", "mu", "nu", "xi", "omicron", "pi",
    "rho", "sigma", "tau", "upsilon", "phi", "chi",
    "psi", "omega",
]


tokens = {
    "Space": r"\s+",
    "Escape": r"\\[^A-Za-z]",
    "Command": r"\\[A-Za-z0-9]+",
    "OpenBrace": r"\{",
    "CloseBrace": r"\}",
}


class Command(object):
  def __init__(self, name):
    self._name = name
    self._args = []

  def append(self, arg):
    self._args.append(arg)


class Raw(object):
  def __init__(self):
    self._content = ""

  def append(self, text):
    self._content += text


class MathManager(object):
  def __init__(self):
    self._python_mark = python_mark
    self._instruction_mark = instruction_mark
    self._line_splitter = line_splitter
    self._space_holder = space_holder
    self._indent = math_indent
    self._locals = {}
    self._equation_name = None
    self._meta = []
    self.common_definitions()
    self.define_define_functions()

  def get(self, key):
    return self._locals[key]

  def set_local_variables(self, variables):
    for key, value in variables.items():
      self._locals[key] = value

  def define(self, key, value):
    self._locals[key] = value

  def add_meta(self, line):
    if line not in self._meta:
      self._meta.append(line)

  def define_latex(self, command, content):
    if command in ["vec", "emph"]:
      name = "renewcommand"
    else:
      name = "newcommand"

    if "#" not in content:
      self.add_meta(r"\%s{\%s}{%s}" % (name, command, content))
      return
    nargs = 0
    for i in range(1, 10):
      if content.find(f"#{i}") >= 0:
        nargs = i
    if nargs == 0:
      self.add_meta(r"\%s{\%s}{%s}" % (name, command, content))
      return
    self.add_meta(r"\%s{\%s}[%d]{%s}" % (name, command, nargs, content))

  def render_meta(self):
    return "\n".join(self._meta)
  
  def define_define_function(self, name):
    f = getattr(self, name)
    def wrap(*args, **kwargs):
      f(*args, **kwargs)
      return ""
    self.define(name.replace("_", ""), wrap)
  
  def define_define_functions(self):
    self.define_define_function("define_sf")
    self.define_define_function("define_cal")
    self.define_define_function("define_bb")
    self.define_define_function("define_bbm")
    self.define_define_function("define_bf")
    self.define_define_function("define_tt")
    self.define_define_function("define_rm")
    self.define_define_function("define_bd")
    def define_func(key, value):
      if "#" in value:
        self.define(key, str_to_function(value))
      else:
        self.define(key, value)
      return ""
    self.define("define", define_func)

  def define_sf(self, content, alias=None):
    if alias is not None:
      self.define(alias, r"\mathsf{%s}" % content)
    else:
      self.define(content, r"\mathsf{%s}" % content)

  def define_cal(self, content, alias=None):
    if alias is not None:
      self.define(alias, r"\mathcal{%s}" % content)
    else:
      self.define(content, r"\mathcal{%s}" % content)

  def define_bb(self, content, alias=None):
    if alias is not None:
      self.define(alias, r"\mathbb{%s}" % content)
    else:
      self.define(content, r"\mathbb{%s}" % content)

  def define_bbm(self, content, alias=None):
    if alias is not None:
      self.define(alias, r"\mathbbm{%s}" % content)
    else:
      self.define(content, r"\mathbbm{%s}" % content)

  def define_bf(self, content, alias=None):
    if alias is not None:
      self.define(alias, r"\mathbf{%s}" % content)
    else:
      self.define(content, r"\mathbf{%s}" % content)

  def define_tt(self, content, alias=None):
    if alias is not None:
      self.define(alias, r"\mathtt{%s}" % content)
    else:
      self.define(content, r"\mathtt{%s}" % content)

  def define_rm(self, content, alias=None):
    if alias is not None:
      self.define(alias, r"\mathrm{%s}" % content)
    else:
      self.define(content, r"\mathrm{%s}" % content)

  def define_bd(self, content, alias=None):
    if alias is not None:
      self.define(alias, r"\boldsymbol{%s}" % content)
    else:
      self.define(content, r"\boldsymbol{%s}" % content)

  def common_definitions(self):
    self.define("paren", lambda v: r"\left(%s\right)" % v)
    self.define("bracket", lambda v: r"\left[%s\right]" % v)
    self.define("brace", lambda v: r"\left\{%s\right\}" % v)
    self.define("vecsub", lambda a, b: r"\vec{%s}_{[%s]}" % (a, b))
    self.define("isequal", r"\stackrel{?}{=}")
    self.define("sample", r"\stackrel{\$}{\gets}")
    for a in list(string.ascii_uppercase):
      self.define_rm(a, f"rm{a}")
      self.define_bb(a, f"bb{a}")
      self.define_bf(a, f"bf{a}")
      self.define_cal(a, f"c{a}")
      self.define_sf(a, f"sf{a}")
      self.define_tt(a, f"tt{a}")
      self.define_bd(a, f"bd{a}")
    for a in list(string.ascii_lowercase):
      self.define_rm(a, f"rm_{a}")
      self.define_bb(a, f"bb_{a}")
      self.define_bf(a, f"bf_{a}")
      self.define_cal(a, f"c_{a}")
      self.define_sf(a, f"sf_{a}")
      self.define_tt(a, f"tt_{a}")
      self.define_bd(a, f"bd_{a}")
    for g in greek_letters:
      self.define(g, "\\"+g)
      g = g.capitalize()
      self.define(g, "\\"+g)
      self.define_rm("\\"+g, f"rm{g}")
      self.define_bb("\\"+g, f"bb{g}")
      self.define_bf("\\"+g, f"bf{g}")
      self.define_cal("\\"+g, f"cal{g}")
      self.define_sf("\\"+g, f"sf{g}")
      self.define_tt("\\"+g, f"tt{g}")
      self.define_bd("\\"+g, f"bd{g}")

  def common_definitions_for_crypto(self):
    self.define("field", self.get("bbF"))
    self.define("ffv", lambda e: self(r"\field^{%s}" % e))
    self.define("setup", self.get("sfG"))
    self.define("prover", self.get("sfP"))
    self.define("verifier", self.get("sfV"))
    self.define("indexer", self.get("sfI"))
    self.define("extractor", self.get("sfE"))
    self.define("adversary", self.get("sfA"))
    self.define("simulator", self.get("sfS"))
    self.define("index", r"\mathbbm{i}")
    self.define("instance", r"\mathbbm{x}")
    self.define("witness", r"\mathbbm{w}")

  def __call__(self, content):
    return self.transpile(self.preprocess(self.parse(content)))

  def view(self, content, env):
    if isnotebook():
      content = self(content)
      if env == "$":
        content = f"${content}$"
      elif env == "\\[":
        content = f"\\[{content}\\]"
      else:
        content = f"\\begin{{{env}}}\n{content}\n\\end{{{env}}}"
      return genpng(content, meta=self.render_meta())
    else:
      return None

  def parse(self, content):
    lines = content.split("\n")
    lines = [(i+1, self.compute_level(i+1, line), line.strip())
             for i, line in enumerate(lines)
             if len(line.strip()) > 0]
    return lines

  def compute_level(self, i, line):
    spaces = len(line) - len(line.lstrip())
    if spaces % self._indent != 0:
      raise MathEquationError(f"Line {i} is not indented with "
                              f"multiples of {self._indent}")
    return spaces // self._indent

  def preprocess(self, lines):
    ret = []
    for i, level, line in lines:
      try:
        processed_lines = self.process_line(line, level)
      except MathEquationError as e:
        raise MathEquationError(
            "Preprocess Error in processing line {i}:\n{line}\nError: {e}")
      for level, processed_line in processed_lines:
        if len(processed_line) > 0:
          ret.append((i, level, processed_line))
    return ret

  def process_line(self, line, level):
    if line.find(self._line_splitter) > 0:
      ret = []
      current_level = level
      while len(line) > 0:
        index = line.find(self._line_splitter)
        if index < 0:
          processed_lines = self.process_line(line, current_level)
          assert len(processed_lines) <= 1
          if len(processed_lines) == 1:
            processed_level, processed_line = processed_lines[0]
            ret.append((processed_level, processed_line))
          break
        if index == 0:
          current_level -= 1
          if current_level < 0:
            raise MathEquationError("Level is below zero!")
          line = line[len(self._line_splitter):]
          continue
        processed_lines = self.process_line(line[:index], current_level)
        assert len(processed_lines) <= 1
        if len(processed_lines) == 1:
          processed_level, processed_line = processed_lines[0]
          ret.append((processed_level, processed_line))
        line = line[index+len(self._line_splitter):]
        if len(ret) > 0 and ret[-1][1].find(' ') >= 0:
          current_level += 1
      return ret
    if line.startswith(self._python_mark):
      code = line[len(self._python_mark):]
      try:
        line = str(eval(code, self._locals if self._locals else {}))
      except Exception as e:
        raise e
      return [(level, line)]
    if line.startswith(self._instruction_mark):
      code = line[len(self._instruction_mark):]
      code = code.strip().split(" ")
      if code[0] == "name":
        self._equation_name = " ".join(code[1:])
      return []
    return [(level, line)]

  def transpile(self, lines):
    ret = []
    stack = []
    for i, level, line in lines:
      while len(stack) > level:
        ret.append(stack.pop())
      if level == len(stack):
        index = line.find(' ')
        if index > 0:
          ret.append(line[:index])
          stack.append(line[index+1:])
        else:
          ret.append(line)
      else:
        raise MathEquationError(
            f"Line {i} over indented:\n{line}\nExpected {len(stack)}, "
            f"got {level}")
    while len(stack) > 0:
      ret.append(stack.pop())

    return self.post_process("".join(ret))

  def tokenize(self, line):
    if len(line) == 0:
      return "End", "", ""
    for label, token in tokens.items():
      match = re.match(token, line)
      if match:
        return label, match.group(0), line[match.span()[1]:]
    return "Char", line[0], line[1:]

  def post_process(self, line):
    line = line.replace(self._space_holder, " ")
    stack, mode = [Raw()], "normal"
    label, token, line = self.tokenize(line)
    while True:
      if mode == "normal":
        """
        In this mode, the top of the stack must be Raw,
        otherwise something is wrong
        """
        if label in ["Space", "Escape", "Char"]:
          stack[-1].append(token)
        elif label == "Command":
          stack.append(Command(token[1:]))
          mode = "expect open"
        elif label == "OpenBrace":
          stack.append(Raw())
        elif label == "CloseBrace":
          last = stack[-1]._content
          stack.pop()
          if len(stack) == 0:
            raise MathEquationError("Extra }")
          if isinstance(stack[-1], Command):
            stack[-1].append(last)
          else:
            stack[-1].append("{%s}" % last)
          mode = "just closed"
        elif label == "End":
          if len(stack) > 1:
            raise MathEquationError("Unexpected End, expecting '}'")
          return stack[0]._content
        else:
          raise ValueError(f"Unknown label {label}")
      elif mode == "expect open":
        if label == "OpenBrace":
          stack.append(Raw())
          mode = "normal"
        elif label == "Space":
          pass
        else:
          command = stack[-1]._name
          stack.pop()
          assert len(stack) > 0
          if command in self._locals:
            """
            This means a command does not receive any parameter.
            In this case, this command must be mapped directly to string.
            """
            stack[-1].append(str(self._locals[command]))
          else:
            stack[-1].append("\\" + command)
          mode = "normal"
          continue
      elif mode == "just closed":
        if label == "OpenBrace":
          stack.append(Raw())
          mode = "normal"
        else:
          if isinstance(stack[-1], Command):
            command = stack[-1]._name
            if command in self._locals:
              if isinstance(self._locals[command], str):
                if (len(stack[-1]._args) != 1 or
                    stack[-1]._args[0].strip() != ''):
                  raise MathEquationError(
                      f"Invoke a string with arguments {stack[-1]._args}")
                val = self._locals[command] + "{}"
              else:
                val = self._locals[command](*stack[-1]._args)
            else:
              val = "\\" + command + "" .join(["{%s}" % arg
                                               for arg in stack[-1]._args])
            stack.pop()
            assert isinstance(stack[-1], Raw)
            stack[-1].append(val)
          mode = "normal"
          continue
      else:
        raise ValueError(f"Impossible mode {mode}")

      label, token, line = self.tokenize(line)
