import re
from juptex.text import TextManager


class ParagraphManager(object):
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

  def __call__(self, content):
    lines = content.split("\n")
    lines = [line for line in lines if line.strip() != ""]
    lists = self._split_by_lists(lines)
    return "\n".join(self._dump_colist(lists, 0))

  def _split_by_lists(self, lines):
    ret = CollectionListSentences()
    for line in lines:
      if line.lstrip().startswith("- ") or line.lstrip().startswith("* "):
        indent = len(line) - len(line.lstrip())
        line = line.lstrip()
        prefix_len = len(line) - len(line[2:].lstrip())
        line = line[2:].lstrip()
        to_append = self._ensure_environment(ret, "itemize",
                                             indent, prefix_len)
        to_append.append(Sentence(line, indent + prefix_len))
      elif re.match(r"\d+\. ", line.lstrip()):
        indent = len(line) - len(line.lstrip())
        line = line.lstrip()
        prefix_len = len(line) - len(line[line.find(" ")+1:].lstrip())
        line = line[line.find(" ")+1:].lstrip()
        to_append = self._ensure_environment(ret, "enumerate",
                                             indent, prefix_len)
        to_append.append(Sentence(line, indent + prefix_len))
      else:
        indent = len(line) - len(line.lstrip())
        self._append_sentence_to_colist(ret, line.lstrip(), indent)
    return ret

  def _ensure_environment(self, colist, category, indent, prefix_len):
    """
    Three situations:
    1. create a new list after the last item because the last item is sentence
    2. create a new list after the last item because the last item is a
       different list and does not reach the threshold
    3. append in the last item because the last item is a list and the
       indent level reaches the indentation threshold of the last item
    The indentation threshold of a list is the starting position of the
    last sentence in this list (after the prefix is removed)
    """
    if colist.last_is_list():
      threshold = colist.last().last().threshold()
      if indent >= threshold:
        return self._ensure_environment(colist.last().last(), category,
                                        indent, prefix_len)
      if colist.last().iscategory(category):
        list_item = ListItem(indent + prefix_len)
        colist.last().append(list_item)
        return list_item

    ls = List(category)
    list_item = ListItem(indent + prefix_len)
    ls.append(list_item)
    colist.append(ls)
    return list_item

  def _append_sentence_to_colist(self, colist, line, indent):
    if colist.empty() or (colist.last_is_list() and
                          indent < colist.last().last().threshold()):
      colist.append(Sentence(line, indent))
      return

    if colist.last_is_list() and indent >= colist.last().last().threshold():
      self._append_sentence_to_colist(colist.last().last(), line, indent)
      return

    assert isinstance(colist.last(), Sentence)
    indent_level = colist.last()._indent_level
    extra_indent = max(0, indent - indent_level)
    colist.last()._content += "\n" + " " * extra_indent + line

  def _dump_colist(self, colist, indent):
    ret = []
    for i, item in enumerate(colist._content):
      if isinstance(item, Sentence):
        sentence = self._text_manager(item._content)
        if i == 0:
          ret.append(sentence)
        else:
          ret.append(" " * indent + sentence)
      else:
        assert i > 0  # The first item must be sentence
        body = "\n".join([" " * indent + r"\item " +
                          "\n".join(self._dump_colist(list_item, indent + 2))
                          for list_item in item._items])
        ret.append(r"""%s\begin{%s}
%s
%s\end{%s}""" % (" " * indent, item._category, body,
                 " " * indent, item._category))
    return ret


class Sentence(object):
  def __init__(self, content, indent_level):
    self._content = content
    self._indent_level = indent_level


class List(object):
  def __init__(self, category):
    self._category = category
    self._items = []

  def iscategory(self, category):
    return self._category == category

  def append(self, item):
    assert isinstance(item, ListItem)
    self._items.append(item)

  def empty(self):
    return len(self._items) == 0

  def last(self):
    if self.empty():
      return None
    return self._items[-1]


class CollectionListSentences(object):
  def __init__(self):
    self._content = []

  def append(self, item):
    assert isinstance(item, Sentence) or isinstance(item, List)
    self._content.append(item)

  def empty(self):
    return len(self._content) == 0

  def last(self):
    if self.empty():
      return None
    return self._content[-1]

  def last_is_not_list(self):
    return self.empty() or not isinstance(self.last(), List)

  def last_is_list(self):
    return not self.empty() and isinstance(self.last(), List)

  def threshold(self):
    return 0


class ListItem(CollectionListSentences):
  def __init__(self, indent_threshold):
    super().__init__()
    self._indent_threshold = indent_threshold

  def threshold(self):
    return self._indent_threshold
