import unittest
from juptex.keywords import *


class TestKeywords(unittest.TestCase):
  def test_compile(self):
    keywords = Keywords()
    keywords.add_keyword("Key")
    keywords.add_keyword("Word")
    self.assertEqual(keywords.dump(), r"\keywords{Key, Word}")


if __name__ == "__main__":
  unittest.main()
