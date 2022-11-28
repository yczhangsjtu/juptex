import re
from pybtex.database import parse_file, BibliographyData
from juptex.config import *


class Reference(object):
  def __init__(self):
    self.database = parse_file(bib_path)
    self.filtered_database = BibliographyData()

  def extract_citations(self, content):
    while True:
      match = re.search(r"\\cite\{([\w\-]+(:?,\s*[\w\-]+)*)\}", content)
      if match:
        key = match.group(1)
        keys = key.split(',')
        for key in keys:
          key = key.strip()
          if key not in self.database.entries:
            raise Exception(f"Unfound citation: {key}")
          entry = self.database.entries[key]
          for field in reference_entry_black_list:
            if field in entry.fields:
              del entry.fields[field]
          self.filtered_database.entries[key] = entry
        content = content[match.span()[1]:]
      else:
        break

  def dump(self, path):
    if len(self.filtered_database.entries) > 0:
      with open(path, "w") as f:
        self.filtered_database.to_file(f)
