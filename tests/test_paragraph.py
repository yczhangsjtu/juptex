import unittest
from juptex.paragraph import *


class TestParagraph(unittest.TestCase):
  def test_compile(self):
    pm = ParagraphManager()
    pm.common_definitions_for_crypto()
    self.assertEqual(pm(r"""
First line:
- List1
1. List2
   - List3
   - Item.
     Item Continue $\field$.
2. Test2. Something.
   Hello.
3. Test3. Something _else_.
   Something else.
Last line.
"""), r"""First line:
\begin{itemize}
\item List1
\end{itemize}
\begin{enumerate}
\item List2
  \begin{itemize}
  \item List3
  \item Item.
Item Continue $\mathbb{F}$.
  \end{itemize}
\item Test2. Something.
Hello.
\item Test3. Something \emph{else}.
Something else.
\end{enumerate}
Last line.""")


if __name__ == "__main__":
  unittest.main()
