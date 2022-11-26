import unittest
from juptex.figure import *


class TestFigure(unittest.TestCase):
  def test_compile(self):
    fm = FigureManager()
    fm.common_definitions_for_crypto()
    self.assertEqual(fm("data/Algebra.png",
                        r"Galios Theory for $\bbQ$",
                        "fig:algebra"),
                     r"""\begin{figure}[ht]
  \includegraphics[width=\textwidth]{images/Algebra.png}
  \caption{Galios Theory for $\mathbb{Q}$}\label{fig:algebra}
\end{figure}""")


if __name__ == "__main__":
  unittest.main()
