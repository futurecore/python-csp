from base import BaseCspTest, main
from csp.csp import Par

class TestPar(BaseCspTest):

    def test_process_object(self):
        Par(*[self.proc(x) for x in range(5)]).start()
        self.assertEqual(''.join(sorted(self.output())), '01234')

    def test_supports_nesting(self):
        _ = self.proc
        Par(_(0), Par(_(1), _(2)), Par(_(3), Par(_(4), _(5)))).start()
        self.assertEqual(''.join(sorted(self.output())), '012345')


class TestMixinFloordivOperator(BaseCspTest):

    def test_floordiv_runs_parallel(self):
        _ = self.proc
        _(0) // (_(1), _(2), _(3), _(4))
        self.assertEqual(''.join(sorted(self.output())), '01234')

    def does_not_work_with_non_tuple(self):
        # Why not?
        _ = self.proc
        _(0) // _(1)
        self.assertEqual(''.join(sorted(self.output())), '01')


class TestMixParObjectAndFloordivOperator(BaseCspTest):

    def test_mixed_syntax(self):
        _ = self.proc
        _(0) // (Par(_(1), _(2)), _(3))
        self.assertEqual(''.join(sorted(self.output())), '0123')


if __name__ == '__main__':
    main()
