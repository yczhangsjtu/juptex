import unittest
from juptex.utils import *

class TestFindFirstUnescapedQuote(unittest.TestCase):
  def test_count_slashes(self):
    self.assertEqual(count_slashes('hello world', -1), 0)
    self.assertEqual(count_slashes('hello world', 0), 0)
    self.assertEqual(count_slashes('hello world', 5), 0)
    self.assertEqual(count_slashes(r'hello \world', 6), 1)
    self.assertEqual(count_slashes(r'hello \\world', 6), 1)
    self.assertEqual(count_slashes(r'hello \\world', 7), 2)
    self.assertEqual(count_slashes(r'hello \\world', 8), 0)
    self.assertEqual(count_slashes(r'hello \\\\world', 5), 0)
    self.assertEqual(count_slashes(r'hello \\\\world', 6), 1)
    self.assertEqual(count_slashes(r'hello \\\\world', 7), 2)
    self.assertEqual(count_slashes(r'hello \\\\world', 8), 3)
    self.assertEqual(count_slashes(r'hello \\\\world', 9), 4)
    self.assertEqual(count_slashes(r'hello \\\\world', 10), 0)
    
  def test_find_first_unescaped_quote(self):
    self.assertEqual(find_first_unescaped_quote('hello world'), -1)
    self.assertEqual(find_first_unescaped_quote('hello "world'), 6)
    self.assertEqual(find_first_unescaped_quote(r'hello \"world'), -1)
    self.assertEqual(find_first_unescaped_quote(r'hello "wor\\"ld'), 6)
    self.assertEqual(find_first_unescaped_quote(r'hello \"wor\\"ld'), 13)

if __name__ == '__main__':
  unittest.main()