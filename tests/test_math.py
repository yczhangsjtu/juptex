import unittest
from juptex.matheq import *


class TestMathEq(unittest.TestCase):
  def test_compile(self):
    mm = MathManager()
    mm.common_definitions_for_crypto()
    mm.set_local_variables(locals())
    mm.define_sf("CompCirc")
    self.assertEqual(
        mm(r"C\in\CompCirc,\vec{x}\in\ffv{\ell_1},\vec{y}\in\ffv{\ffv{2}}"),
        r"C\in\mathsf{CompCirc},\vec{x}\in\mathbb{F}^{\ell_1},"
        r"\vec{y}\in\mathbb{F}^{\mathbb{F}^{2}}"
    )
    self.assertEqual(
        mm(r"""
f( ):=
  X
\left| \right.
  \begin{array} \end{array}
    \frac{\CompCirc}{\ffv{abc}}
  """),
        r"f(X):=\left|\begin{array}"
        r"\frac{\mathsf{CompCirc}}{\mathbb{F}^{abc}}\end{array}\right.")
    mm.define_sf("SubCirc")
    mm.define_rm("offline")
    self.assertEqual(
        mm(r"\SubCirc_{\offline}"),
        r"\mathsf{SubCirc}_{\mathrm{offline}}"
    )
    self.assertEqual(mm(r"""
\definesf{test}
\define{vec}{\boldsymbol{\mathsf{#1}}}
\define{vtest}{\vec{\test}}
\test
"""), r"\mathsf{test}")
    self.assertEqual(mm(r"\vtest"), r"\boldsymbol{\mathsf{\mathsf{test}}}")


if __name__ == "__main__":
  unittest.main()
