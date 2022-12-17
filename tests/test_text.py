import unittest
from juptex.text import *


class TestText(unittest.TestCase):
  def test_compile(self):
    tm = TextManager()
    test_var = "Hello"
    tm.set_local_variables(locals())
    self.assertEqual(tm(""), "")
    self.assertEqual(tm(r"""
Hello world, hello world, hello world.
Hello world, hello world, hello world.
Hello world, hello world, hello world.
Hello world, hello world, hello world.
"""), r"""
Hello world, hello world, hello world.
Hello world, hello world, hello world.
Hello world, hello world, hello world.
Hello world, hello world, hello world.
""")
    self.assertEqual(tm(r"""
Hello "_world_", hello "wo\"rld", hello world.
Hello [[world]], **hello world**, hello world.
Hello <u>world</u> $\sfC$, hello \"world `test_var`, hello world.
<span hidden>Hello world</span>, "hello world", `2**5` hello world $$\bbAlpha$$.
"""), r"""
Hello ``\emph{world}'', hello ``wo\"rld'', hello world.
Hello~\cite{world}, \textbf{hello world}, hello world.
Hello \underline{world} $\mathsf{C}$, hello \"world Hello, hello world.
, ``hello world'', 32 hello world \[\mathbb{\Alpha}\].
""")


if __name__ == "__main__":
  unittest.main()
