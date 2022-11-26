import unittest
from juptex.matheq import *


class TestMathEq(unittest.TestCase):
  def test_compile(self):
    mm = MathManager()
    mm.common_definitions_for_crypto()
    mm.set_local_variables(locals())
    mm.define_sf("CompCirc")
    self.assertEqual(
        mm(r"C\in\CompCirc,\vec{x}\in\ffv{\ell_1},\vec{y}\in\ffv{\ell_2}"),
        r"C\in\mathsf{CompCirc},\vec{x}\in\mathbb{F}^{\ell_1},"
        r"\vec{y}\in\mathbb{F}^{\ell_2}"
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


if __name__ == "__main__":
  unittest.main()
