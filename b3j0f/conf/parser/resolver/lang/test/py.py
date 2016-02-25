from ..py import resolvepy

from b3j0f.utils.ut import UTCase

from unittest import main


class Test(UTCase):

    def test_safe(self):

        self.assertRaises(
            NameError, resolvepy, expr='open', safe=True, besteffort=False
        )

    def test_unsafe(self):

        result = resolvepy(expr='open', safe=False, besteffort=False)

        self.assertIs(open, result)

    def test_tostr(self):

        result = resolvepy(
            expr='open', safe=False, tostr=True, besteffort=False
        )

        self.assertEqual(result, str(open))

    def test_scope(self):

        self.assertRaises(NameError, resolvepy, expr='test', besteffort=False)

        result = resolvepy(expr='test', scope={'test': 1})

        self.assertEqual(result, 1)

    def test_besteffort(self):

        test = 'b3j0f.conf.configurable.log.Logger'

        self.assertRaises(
            NameError, resolvepy, expr=test, besteffort=False
        )

        resolvepy(expr=test, besteffort=True)


if __name__ == '__main__':
    main()
