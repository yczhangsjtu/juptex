from contextlib import contextmanager
from juptex.errors import *
from juptex.utils import *
from juptex.text import TextManager


class AlgorithmManager(object):
  def __init__(self, text_manager=None, math_manager=None):
    self._text_manager = (text_manager if text_manager is not None
                          else TextManager(math_manager))
    self._locals = self._text_manager._locals
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

  def __call__(self, content, name):
    lines = content.split("\n")
    line_info = []
    for line in lines:
      line_info.append(self._preprocess_line(line))
    root = self._form_tree(line_info)
    empty_count = 0
    algorithmics = []
    left_algorithmics = algorithmics
    right_algorithmics = []
    title = None
    while root is not None:
      tp = root["type"]
      if tp == "title":
        title = self._concatenate_all_child(root)
        empty_count = 0
      elif tp == "empty":
        empty_count += 1
      elif tp == "vspace":
        algorithmics.append(r"\vspace{%s}" % root["content"])
        empty_count = 0
      else:
        if empty_count >= 3:
          algorithmics = right_algorithmics
        if len(algorithmics) == 0 or empty_count >= 2 or \
           not isinstance(algorithmics[-1], AlgorithmicEditor):
          algorithmic = AlgorithmicEditor()
          algorithmics.append(algorithmic)
        else:
          algorithmic = algorithmics[-1]
        empty_count = 0
        self._process_node(algorithmic, root)
      root = root["next"]

    if title is None:
      raise ValueError("No title")
    if len(right_algorithmics) > 0:
      return r"""\begin{figure*}[ht!]
\fbox{
\begin{minipage}{0.5\textwidth}
%s
\end{minipage}
\hspace{0.5cm}
\begin{minipage}{0.5\textwidth}
%s
\end{minipage}
}
\caption{%s}\label{fig:%s}
\end{figure*}""" % ("\n\n".join([alg.render()
                                 if isinstance(alg, AlgorithmicEditor)
                                 else alg for alg in left_algorithmics]),
                    "\n\n".join([alg.render()
                                 if isinstance(alg, AlgorithmicEditor)
                                 else alg for alg in right_algorithmics]),
                    title, to_label(name))
    else:
      return r"""\begin{algorithm}
\caption{%s}\label{alg:%s}
%s
\end{algorithm}""" % (
          title, to_label(name),
          "\n\n".join([alg.render()
                       if isinstance(alg, AlgorithmicEditor) else alg
                       for alg in algorithmics]))

  def _concatenate_all_child(self, node, include_next=False):
    if node is None:
      return None
    ret = node["content"]
    if ret == "```math":
      child = self._concatenate_math_equation(node["child"], 0)
      assert child is not None
      ret = "$%s$" % self._text_manager._math_manager(child)
    else:
      child = self._concatenate_all_child(node["child"], include_next=True)
      if child is not None:
        ret = f"{ret} {child}"
    if include_next:
      nxt = self._concatenate_all_child(node["next"], include_next=True)
      if nxt is not None:
        ret = f"{ret} {nxt}"
    return ret

  def _concatenate_math_equation(self, node, indent):
    if node is None:
      return None
    ret = "  " * indent + node["content"]
    child = self._concatenate_math_equation(node["child"], indent + 1)
    if child is not None:
      ret = f"{ret}\n{child}"
    nxt = self._concatenate_math_equation(node["next"], indent)
    if nxt is not None:
      ret = f"{ret}\n{nxt}"
    return ret

  def _process_node(self, algorithmic, node, include_next=False):
    tp = node["type"]
    if tp == "statement":
      content = self._concatenate_all_child(node)
      algorithmic.statement(self._text_manager(content))
    elif tp == "comment":
      content = self._concatenate_all_child(node)
      algorithmic.line_comment(self._text_manager(content))
    elif tp == "func":
      func_name, args = node["content"]
      assert node["child"] is not None
      with algorithmic.procedure(func_name, args):
        self._process_node(algorithmic, node["child"], include_next=True)
    elif tp == "if":
      assert node["child"] is not None
      with algorithmic.if_cond(node["content"]):
        self._process_node(algorithmic, node["child"], include_next=True)
    elif tp == "elif":
      assert node["child"] is not None
      with algorithmic.else_if(node["content"]):
        self._process_node(algorithmic, node["child"], include_next=True)
    elif tp == "else":
      assert node["child"] is not None
      with algorithmic.add_else():
        self._process_node(algorithmic, node["child"], include_next=True)
    elif tp == "for":
      assert node["child"] is not None
      with algorithmic.for_loop(node["content"]):
        self._process_node(algorithmic, node["child"], include_next=True)
    elif tp == "continue":
      algorithmic.continue_loop()
    elif tp == "return":
      algorithmic.func_return(node["content"])
    elif tp == "empty":
      pass
    else:
      raise ValueError(f"Unexpected type: {tp}")

    if include_next and node["next"] is not None:
      self._process_node(algorithmic, node["next"], include_next=True)

  def _preprocess_line(self, line):
    content = line.lstrip()
    indent = (len(line) - len(content)) // 2
    if content.startswith("if "):
      assert content.endswith(":")
      tp = "if"
      content = content[3:-1]
    elif content.startswith("title: "):
      tp = "title"
      content = content[7:]
    elif content.startswith("vspace: "):
      tp = "vspace"
      content = content[8:]
    elif content == "else:":
      tp = "else"
      content = None
    elif content.startswith("elif "):
      assert content.endswith(":")
      tp = "elif"
      content = content[5:-1]
    elif content.startswith("def "):
      assert content.endswith("):")
      tp = "func"
      content = content[4:-2]
      left_paren = content.find("(")
      assert left_paren > 0
      func_name = content[:left_paren]
      args = content[left_paren+1:]
      content = (func_name, args)
    elif content.startswith("for "):
      assert content.endswith(":")
      tp = "for"
      content = content[4:-1]
    elif content == "continue":
      tp = "continue"
      content = None
    elif content == "return":
      tp = "return"
    elif content.startswith("\\if"):
      tp = "statement"
      content = content[1:]
    elif content.startswith("\\for"):
      tp = "statement"
      content = content[1:]
    elif content.startswith("\\return"):
      tp = "statement"
      content = content[1:]
    elif content.startswith("\\continue"):
      tp = "statement"
      content = content[1:]
    elif content.startswith("\\else"):
      tp = "statement"
      content = content[1:]
    elif content.startswith("\\elif"):
      tp = "statement"
      content = content[1:]
    elif content.startswith("//"):
      tp = "comment"
      content = content[2:].lstrip()
    elif len(content) == 0:
      tp = "empty"
      content = None
    else:
      tp = "statement"

    return indent, tp, content

  def _make_node(self, tp, content):
    return {
        "type": tp,
        "content": content,
        "next": None,
        "child": None,
    }

  def _form_tree(self, line_info, base_indent=0):
    curr_node, ret = None, None
    curr = 0
    while curr < len(line_info):
      indent, tp, content = line_info[curr]
      assert indent >= base_indent or tp == "empty"
      if indent == base_indent:
        node = self._make_node(tp, content)
        if curr_node is not None:
          curr_node["next"] = node
        else:
          ret = node
        curr_node = node
        curr += 1
      else:
        for i in range(curr, len(line_info)):
          until = i + 1
          indent1, tp1, _ = line_info[i]
          if indent1 < indent and tp1 != "empty":
            until = i
            break
        while line_info[until-1][1] == "empty":
          """
          Empty lines at the end of the child should be considered
          as in current level. Empty lines are important, because
          we will use two empty lines as dividers between algorithmics,
          and three empty lines as dividers between columns in a wide
          algorithm.
          """
          until -= 1
        node = self._form_tree(line_info[curr:until], base_indent=indent)
        assert curr_node is not None
        curr_node["child"] = node
        curr = until
    return ret


class AlgorithmicEditor(object):

  """An algorithmic block in the paper."""

  def __init__(self):
    """Initialized to be empty."""
    self._content = []
    self._indent = 0

  def indent(self):
    self._indent += 1

  def deindent(self):
    assert self._indent > 0
    self._indent -= 1

  def add_raw(self, s):
    self._content.append(s)

  def eol(self):
    self.add_raw("\n" + "  " * self._indent)

  def eol_not_start(self):
    if len(self._content) > 0:
      self.eol()

  def eol_indent(self):
    self.indent()
    self.eol()

  def eol_deindent(self):
    self.deindent()
    self.eol()

  @contextmanager
  def procedure(self, name, arguments):
    self.eol_not_start()
    self.add_raw(r"\Procedure{")
    self.add_raw(name)
    self.add_raw("}{")
    self.add_raw(arguments)
    self.add_raw("}")
    self.indent()
    yield
    if self._content[-1] == ";":
      self._content[-1] = "."
    self.eol_deindent()
    self.add_raw(r"\EndProcedure")

  @contextmanager
  def for_loop(self, content):
    self.eol_not_start()
    self.add_raw(r"\For{")
    self.add_raw(content)
    self.add_raw("}")
    self.indent()
    yield
    self.eol_deindent()
    self.add_raw(r"\EndFor")

  @contextmanager
  def if_cond(self, content):
    self.eol_not_start()
    self.add_raw(r"\If{")
    self.add_raw(content)
    self.add_raw("}")
    self.indent()
    yield
    self.eol_deindent()
    self.add_raw(r"\EndIf")

  def else_if(self, content):
    self.eol_deindent()
    self.add_raw(r"\ElsIf{")
    self.add_raw(content)
    self.add_raw("}")
    self.indent()

  def add_else(self):
    self.eol_deindent()
    self.add_raw(r"\Else")
    self.indent()

  def continue_loop(self):
    self.eol_not_start()
    self.add_raw(r"\State \textbf{continue}")
    self.add_raw(";")

  def func_return(self, content=None):
    self.eol_not_start()
    self.add_raw(r"\State \Return")
    if content is not None:
      self.add_raw(" ")
      self.add_raw(content)
    self.add_raw(";")

  def statement(self, content):
    self.eol_not_start()
    self.add_raw(r"\State ")
    self.add_raw(content)
    self.add_raw(";")

  def line_comment(self, content):
    self.eol_not_start()
    self.add_raw(r"\State \Comment{")
    self.add_raw(content)
    self.add_raw("}")

  def render(self):
    return r"""\begin{algorithmic}
%s
\end{algorithmic}""" % "".join(self._content)
