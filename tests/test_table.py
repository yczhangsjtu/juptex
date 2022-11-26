import unittest
from juptex.table import *


class TestTable(unittest.TestCase):
  def test_compile(self):
    test_var = "Hello"
    tm = TableManager()
    tm.set_local_variables(locals())
    tm.common_definitions_for_crypto()
    tabulars = tm.read("data/test.numbers")
    tabulars[0].get_row(0).set_header()
    tabulars[0].get_row(2).set_top_border(Cline(1, 2))
    tabulars[0].get_column("col2").set_right_border(1)
    self.assertEqual(
        tm(tabulars, r"Test **Table**", "tab:test"),
        r"""\begin{table}[ht]
\caption{Test \textbf{Table}}
\label{tab:test}
\begin{tabular}{cc|c}
\hline

\hline
\multicolumn{3}{l}{\textbf{Header}}\\ \hline
Hello \emph{world}, hello world, hello world.
Hello~\cite{world}, \textbf{hello world}, hello world.
Hello world $\mathsf{C}$, hello world Hello, hello world.
Hello world, ``hello world'', 32 hello world \[\mathbb{\Alpha}\]. & $\mathbb{F}$ & A\\ \cline{1-2}
\multicolumn{2}{l}{B} & C\\
D & \multirow{4}{*}{\multicolumn{2}{l}{E}}\\
F &  & \\
G &  & \\
 &  & \\ \hline

\hline
\end{tabular}
\end{table}""")


if __name__ == "__main__":
  unittest.main()
