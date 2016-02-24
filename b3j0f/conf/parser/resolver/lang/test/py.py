from ..py import resolvepy

from b3j0f.utils.ut import UTCase

from unittest import main


class Test(UTCase):

    def test_safe(self):

        self.assertRaises(Exception, resolvepy, expr='open', safe=True)

    def test_unsafe(self):

        result = resolvepy(expr='open', safe=False)

        self.assertIs(open, result)

    def test_tostr(self):

        result = resolvepy(expr='open', safe=False, tostr=True)

        self.assertEqual(result, str(open))

    def test_scope(self):

        self.assertRaises(Exception, resolvepy, expr='test')

        result = resolvepy(expr='test', scope={'test': 1})

        self.assertEqual(result, 1)

if __name__ == '__main__':
    main()
