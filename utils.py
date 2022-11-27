import re


def to_label(name):
  return name.lower().replace(" ", ".").replace("-", ".")


def to_word(name):
  return name.lower().replace(
      " ", "_"
  ).replace(
      "-", "_"
  ).replace(
      ".", "_"
  ).replace(
      ":", "_"
  )


def extract_html_comment(line):
  comments = []
  while True:
    match = re.search(r"<!\-\-(.+?)\-\->", line)
    if not match:
      break
    comments.append(match.group(1))
    start, end = match.span()
    if (start > 0 and line[start-1] == ' ' and
       end < len(line) and line[end] == ' '):
      """
      Merge the two spaces around the comment
      """
      line = line[:start-1] + line[end:]
    else:
      line = line[:start] + line[end:]
  return line, comments


def find_all_labels(content):
  index = 0
  ret = []
  while True:
    start = content.find(r"\label{", index)
    if start < 0:
      return ret
    start += 7
    end = content.find("}", start)
    ret.append(content[start:end])
    index = end + 1
  return ret


def split_by_empty_lines(lines):
  ret = []
  buffer = []
  for line in lines:
    if line == "":
      if len(buffer) > 0:
        ret.append("\n".join(buffer))
      buffer = []
    else:
      buffer.append(line)
  if len(buffer) > 0:
    ret.append("\n".join(buffer))
  return ret


def map_with_merge(lst, f, g):
  """
  Return a new list lst' with lst'[i] = f(lst[i])
  For two adjacent items lst[i] and lst[i+1],
  the value returned from g(lst'[last], lst[i], lst[i+1]) will replace
  lst'[last] if it is not None
  """
  ret = []
  for i in range(len(lst)):
    if i == 0:
      ret.append(f(lst[i]))
    else:
      new_item = g(ret[-1], lst[i-1], lst[i])
      if new_item is not None:
        ret[-1] = new_item
      else:
        ret.append(f(lst[i]))
  return ret
