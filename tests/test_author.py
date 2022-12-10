import unittest
from juptex.author import *


class TestAuthor(unittest.TestCase):
  def test_compile(self):
    alice = Author("Alice", "alice@gmail.com")
    alice.add_institute(
      Institute("Alice Inc.", country="Human")
    )

    bob = Author("Bob", "bob@bob.edu.cn")
    bob.add_institute(
      Institute("Bob University", country="Virtual")
    )
    bob.add_institute(
      Institute("Bob College", country="Human")
    )

    am = AuthorManager()
    am.add_author(alice)
    am.add_author(bob)

    self.assertEqual(am.dump_lncs(),
                     r"""\newcommand*\samethanks[1][\value{footnote}]{\footnotemark[#1]}
\author{
  Alice\inst{1} \and Bob\inst{2,3}
}
\institute{
  Alice Inc.,\\
  \email{alice@gmail.com} \and
  Bob University,\\
  \email{bob@bob.edu.cn} \and
  Bob College
}""")

    self.assertEqual(am.dump_acm(), r"""\author{Alice}
\affiliation{
  \institution{Alice Inc.}
  \country{Human}
}
\email{alice@gmail.com}
\author{Bob}
\affiliation{
  \institution{Bob University}
  \country{Virtual}
}
\affiliation{
  \institution{Bob College}
  \country{Human}
}
\email{bob@bob.edu.cn}""")

    self.assertEqual(am.dump_blog(), r"""\author{Alice, Bob}""")


if __name__ == "__main__":
  unittest.main()
