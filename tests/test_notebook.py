import unittest
from juptex.notebook import *


class TestNotebook(unittest.TestCase):
  def test_get_cells(self):
    cells = get_cells("data/Test.ipynb")
    self.assertEqual(cells, [
      ("markdown", "# Title"),
      ("markdown", "## Section One"),
      ("markdown", """Test paragraph. Test paragraph. Test paragraph.
Test paragraph. Test paragraph. Test paragraph."""),
      ("markdown", "## Section Two"),
      ("markdown", "Test paragraph. Test paragraph. Test paragraph."),
      ("code", """print("Hello")"""),
      ("markdown", """Test List.
- Test item 1.
- Test item 2.
  1. Test enumerate 1.
  2. Test enumerate 2."""),
      ("markdown", "---"),
      ("markdown", "## Code"),
      ("code", """import math
print("Hello")
a = abs(math.sin(100))""")
    ])


if __name__ == "__main__":
  unittest.main()
