from base import BaseCspTest, main
from csp.csp import Seq

class TestSeq(BaseCspTest):

    def test_process_object(self):
        Seq(*[self.proc(x) for x in range(5)]).start()
        self.assertEqual(self.output(), '01234')

    def test_supports_nesting(self):
        _ = self.proc
        Seq(_(0), Seq(_(1), _(2)), Seq(_(3), Seq(_(4), _(5)))).start()
        self.assertEqual(self.output(), '012345')


class TestMixinGtOperator(BaseCspTest):

    def test_greater_operator_starts_sequence(self):
        _ = self.proc
        _(0) > _(1) > _(2) > _(3) > _(4)
        self.assertEqual(self.output(), '01234')


    def does_not_supports_nesting(self):
        # As the resulting Seq object is immediately started, the syntax
        # does not make sense, when nested
        _ = self.proc
        _(0) > (_(1) > _(2)) > (_(3) > (_(4) > _(5)))
        self.assertEqual(self.output(), '012345')


class TestMixSeqObjectAndGtOperator(BaseCspTest):

    def test_mixed_syntax(self):
        _ = self.proc
        _(0) > Seq(_(1), _(2)) > _(3)
        self.assertEqual(self.output(), '0123')


if __name__ == '__main__':
    main()
