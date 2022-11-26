import unittest
from juptex.algorithm import *


class TestAlgorithm(unittest.TestCase):
  def test_compile(self):
    am = AlgorithmManager()
    am.common_definitions_for_crypto()
    self.assertEqual(am(r"""
title: Common Protocols
def EqualToEqual($[[\vec{a}]],[[\vec{b}]],[[\vec{c}]],[[\vec{d}]],T;\vec{a},\vec{b},\vec{c},\vec{d}$):
  $\indexer$ submits $\vec{t}:=\vec{1}^T\|\vec{0}^{N-T}$
  $\prover$ submits
    ```math
      \vec{q}:=\left. \right\|\vec{0}^{N-T}
        \paren{ }_{i=1}^T
          \frac{\vecsub{c}{i}-\vecsub{d}{i}}{\vecsub{a}{i}-\vecsub{b}{i}}
    where $0/0$ is treated as $0$
  $\verifier$ checks
    $\vec{q}\circ\paren{\vec{a}-\vec{b}}=\vec{t}\circ(\vec{c}-\vec{d})$

vspace: 0.3cm

def Indicator($[[\vec{b}]],[[\vec{v}]],a,T;\vec{b},\vec{v}$):
  $\indexer$ submits $\vec{t}:=\vec{1}^T\|\vec{0}^{N-T}$
  $\prover$ submits
    ```math
      \vec{q}:=\left. \right\|\vec{0}^{N-T}
        \paren{ }_{i=1}^T
          \frac{\vecsub{b}{i}-1}{\vecsub{v}{i}-a}
    where $0/0$ is treated as $0$
  $\verifier$ checks $\vec{b}\circ\paren{\vec{v}-a\cdot\vec{1}}=\vec{0}$ and
    $\vec{b}-\vec{t}=\vec{q}\circ\paren{\vec{v}-a\cdot\vec{1}}$ and
    $\vec{b}=\vec{b}\circ\vec{t}$

vspace: 0.3cm

def DiffIndicator($[[\vec{b}]],[[\vec{v}]],T;\vec{b},\vec{v}$):
  $\indexer$ submits $\vec{t}:=\vec{1}^T\|\vec{0}^{N-T}$ and
                     $\vec{notlast}:=\vec{1}^{T-1}\|\vec{0}^{N-T+1}$ and
                     $\vec{e}_1:=1\|\vec{0}^{N-1}$
  $\prover$ submits
    ```math
      \vec{q}:=\left. \right\|\vec{0}^{N-T+1}
        \paren{ }_{i=1}^{T-1}
          \frac{\vecsub{b}{i+1}}{\vecsub{v}{i+1}-\vecsub{v}{i}}
  $\verifier$ checks $\vec{notlast}\circ\vec{q}^{\to{}1}\circ(\vec{v}^{\to{}1}-\vec{v})=\vec{notlast}\circ\vec{b}^{\to{}1}$
  $\verifier$ checks $\vec{notlast}\circ(\vec{b}^{\to{}1}-\vec{1})\circ(\vec{v}^{\to{}1}-\vec{v})=\vec{0}$
  $\verifier$ checks $\vec{b}\circ\vec{e}_1=\vec{e}_1$ and $\vec{b}=\vec{b}\circ\vec{t}$

vspace: 0.3cm

def Range32($[[\vec{v}]];\vec{v}$):
  $\indexer$ submits $\vec{range16}=(0,1,2\cdots,2^{16}-1)\|\vec{0}^{N-2^{16}}$
  $\prover$ submits $\vec{vl},\vec{vh}$
    where $\vecsub{vl}{i}$ and $\vecsub{vh}{i}$ are respectively
    the lower 16 bits and higher 16 bits of $\vecsub{v}{i}$ for each $i\in[N]$
  $\verifier$ checks $\vec{vl}\subset\vec{range16}$ and
    $\vec{vh}\subset\vec{range16}$
  $\verifier$ checks $\vec{v}=\vec{vl}+2^{16}\cdot\vec{vh}$
""", "Common Protocols"),
                     r"""\begin{algorithm}
\caption{Common Protocols}\label{alg:common.protocols}
\begin{algorithmic}
\Procedure{EqualToEqual}{$[[\vec{a}]],[[\vec{b}]],[[\vec{c}]],[[\vec{d}]],T;\vec{a},\vec{b},\vec{c},\vec{d}$}
  \State $\mathsf{I}$ submits $\vec{t}:=\vec{1}^T\|\vec{0}^{N-T}$;
  \State $\mathsf{P}$ submits $\vec{q}:=\left.\left(\frac{\vec{c}_{[i]}-\vec{d}_{[i]}}{\vec{a}_{[i]}-\vec{b}_{[i]}}\right)_{i=1}^T\right\|\vec{0}^{N-T}$ where $0/0$ is treated as $0$;
  \State $\mathsf{V}$ checks $\vec{q}\circ\left(\vec{a}-\vec{b}\right)=\vec{t}\circ(\vec{c}-\vec{d})$.
\EndProcedure
\end{algorithmic}

\vspace{0.3cm}

\begin{algorithmic}
\Procedure{Indicator}{$[[\vec{b}]],[[\vec{v}]],a,T;\vec{b},\vec{v}$}
  \State $\mathsf{I}$ submits $\vec{t}:=\vec{1}^T\|\vec{0}^{N-T}$;
  \State $\mathsf{P}$ submits $\vec{q}:=\left.\left(\frac{\vec{b}_{[i]}-1}{\vec{v}_{[i]}-a}\right)_{i=1}^T\right\|\vec{0}^{N-T}$ where $0/0$ is treated as $0$;
  \State $\mathsf{V}$ checks $\vec{b}\circ\left(\vec{v}-a\cdot\vec{1}\right)=\vec{0}$ and $\vec{b}-\vec{t}=\vec{q}\circ\left(\vec{v}-a\cdot\vec{1}\right)$ and $\vec{b}=\vec{b}\circ\vec{t}$.
\EndProcedure
\end{algorithmic}

\vspace{0.3cm}

\begin{algorithmic}
\Procedure{DiffIndicator}{$[[\vec{b}]],[[\vec{v}]],T;\vec{b},\vec{v}$}
  \State $\mathsf{I}$ submits $\vec{t}:=\vec{1}^T\|\vec{0}^{N-T}$ and $\vec{notlast}:=\vec{1}^{T-1}\|\vec{0}^{N-T+1}$ and $\vec{e}_1:=1\|\vec{0}^{N-1}$;
  \State $\mathsf{P}$ submits $\vec{q}:=\left.\left(\frac{\vec{b}_{[i+1]}}{\vec{v}_{[i+1]}-\vec{v}_{[i]}}\right)_{i=1}^{T-1}\right\|\vec{0}^{N-T+1}$;
  \State $\mathsf{V}$ checks $\vec{notlast}\circ\vec{q}^{\to{}1}\circ(\vec{v}^{\to{}1}-\vec{v})=\vec{notlast}\circ\vec{b}^{\to{}1}$;
  \State $\mathsf{V}$ checks $\vec{notlast}\circ(\vec{b}^{\to{}1}-\vec{1})\circ(\vec{v}^{\to{}1}-\vec{v})=\vec{0}$;
  \State $\mathsf{V}$ checks $\vec{b}\circ\vec{e}_1=\vec{e}_1$ and $\vec{b}=\vec{b}\circ\vec{t}$.
\EndProcedure
\end{algorithmic}

\vspace{0.3cm}

\begin{algorithmic}
\Procedure{Range32}{$[[\vec{v}]];\vec{v}$}
  \State $\mathsf{I}$ submits $\vec{range16}=(0,1,2\cdots,2^{16}-1)\|\vec{0}^{N-2^{16}}$;
  \State $\mathsf{P}$ submits $\vec{vl},\vec{vh}$ where $\vec{vl}_{[i]}$ and $\vec{vh}_{[i]}$ are respectively the lower 16 bits and higher 16 bits of $\vec{v}_{[i]}$ for each $i\in[N]$;
  \State $\mathsf{V}$ checks $\vec{vl}\subset\vec{range16}$ and $\vec{vh}\subset\vec{range16}$;
  \State $\mathsf{V}$ checks $\vec{v}=\vec{vl}+2^{16}\cdot\vec{vh}$.
\EndProcedure
\end{algorithmic}
\end{algorithm}""")


if __name__ == "__main__":
  unittest.main()
