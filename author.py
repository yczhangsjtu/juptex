class Author(object):

  """An author for a paper."""

  def __init__(self, name, email):
    """Initialize the author.

    :name: Name of the author
    :institutes: Affiliations of the author. String
    :email: Email of the author
    :comment: Footnote to be appended to the author

    """
    self._name = name
    self._institutes = []
    self._email = email
    self._comment = None
    self._numbers = []
    self._comment_reference = None

  def add_institute(self, institute):
    if isinstance(institute, str):
      institute = Institute(institute)
    self._institutes.append(institute)

  def set_comment(self, comment):
    self._comment = comment

  def comment(self):
    return self._comment

  def institute(self, index):
    return self._institutes[index]

  def dump_lncs(self, show_inst=True):
    ret = self._name
    if show_inst:
      ret += "\\inst{%s}" % ",".join([f"{number+1}"
                                      for number in self._numbers])
    if self._comment is not None:
      if self._comment_reference is None:
        ret += f"\\thanks{{{self._comment}}}"
      else:
        ret += f"\\samethanks[{self._comment_reference+1}]"
    return ret

  def dump_acm(self):
    ret = [f"\\author{{{self._name}}}"]
    if self._comment is not None:
      if self._comment_reference is None:
        ret.append(f"\\authornote{{{self._comment}}}")
      else:
        ret.append(f"\\authornotemark[{self._comment_reference+1}]")
    for institute in self._institutes:
      ret.append(institute.dump_acm())
    ret.append(f"\\email{{{self._email}}}")
    return ret

  def dump_blog(self):
    return self._name


class AuthorManager(object):
  def __init__(self):
    self._authors = []
    self._institutes = []
    self._footnotes = []
  
  def dump_anonymous(self, template):
    if template == "lncs":
      return r"\author{}\institute{}"
    return r"\author{}"
  
  def dump(self, template):
    return getattr(self, "dump_" + template)()

  def add_author(self, author):
    self._authors.append(author)
    for institute in author._institutes:
      try:
        index = self._institutes.index(institute)
        author._numbers.append(index)
      except ValueError as e:
        author._numbers.append(len(self._institutes))
        self._institutes.append(institute)
    if author._comment is not None:
      try:
        index = self._footnotes.index(author._comment)
        author._comment_reference = index
      except ValueError as e:
        author._comment_reference = None
        self._footnotes.append(author._comment)
    return author

  def get_emails(self, inst):
    ret = []
    for author in self._authors:
      if author._numbers[0] == inst:
        ret.append(author._email)
    return ret

  def merge_emails(self, emails):
    domains = {}
    for i, email in enumerate(emails):
      index = email.find("@")
      domain = email[index+1:]
      if domain in domains:
        domains[domain].append(i)
      else:
        domains[domain] = [i]
    ret = []
    for domain, indices in domains.items():
      if len(indices) == 1:
        ret.append(emails[indices[0]])
      else:
        ret.append(
            r"\{%s\}@%s" % (
                ",".join([emails[index][:-len(domain)-1]
                          for index in indices]),
                domain
            )
        )
    return ",".join(ret)

  def dump_lncs(self):
    author_list = r" \and ".join([author.dump_lncs(len(self._institutes) > 1)
                                  for author in self._authors])
    institute_list = []
    for i, inst in enumerate(self._institutes):
      if len(self.get_emails(i)) > 0:
        inst = f"""{inst.dump_lncs()},\\\\
  \\email{{{self.merge_emails(self.get_emails(i))}}}"""
      else:
        inst = inst.dump_lncs()
      institute_list.append(inst)
    institute_list = " \\and\n  ".join(institute_list)
    if len(self._authors) == 0:
      return r"\author{}\institute{}"
    return r"""\newcommand*\samethanks[1][\value{footnote}]{\footnotemark[#1]}
\author{
  %s
}
\institute{
  %s
}""" % (author_list, institute_list)

  def dump_acm(self):
    if len(self._authors) == 0:
      return r"\author{}"
    return "\n".join([
        "\n".join(author.dump_acm())
        for author in self._authors
    ])

  def dump_blog(self):
    return r"\author{%s}" % ", ".join([
        author.dump_blog() for author in self._authors])


class Institute(object):
  def __init__(self, name, city=None, state=None, country=None):
    self._name = name
    self._city = city
    self._state = state
    self._country = country
  
  def dump(self, template):
    return getattr(self, "blog_" + template)()
  
  def dump_lncs(self):
    return self._name
  
  def dump_acm(self):
    ret = [r"\institution{%s}" % self._name]
    if self._city is not None:
      ret.append(r"\city{%s}" % self._city)
    if self._state is not None:
      ret.append(r"\state{%s}" % self._state)
    if self._country is not None:
      ret.append(r"\country{%s}" % self._country)
    else:
      raise Exception("Country not provided for acm")
    return "\\affiliation{\n  %s\n}" % "\n  ".join(ret)
  
  def dump_blog(self):
    return self._name