class Keywords(object):

  """The key words of a paper."""

  def __init__(self):
    """Initialized to be empty."""
    self._content = []

  def add_keyword(self, keyword):
    self._content.append(keyword)

  def dump(self):
    if len(self._content) > 0:
      return f"\\keywords{{{', '.join(self._content)}}}"
    return ""
