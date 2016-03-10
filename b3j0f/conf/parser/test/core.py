#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2014 Jonathan Labéjof <jonathan.labejof@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# --------------------------------------------------------------------

"""parser UTs"""

from unittest import main

from b3j0f.utils.ut import UTCase

from ...model.conf import Configuration, configuration
from ...model.cat import category
from ...model.param import Parameter
from ..core import (
    REGEX_REF, REGEX_FORMAT, REGEX_STR, REGEX_EXPR,
    parse, serialize, _ref, ParserError, _strparser
)


class RegexRefTest(UTCase):
    """Test the regex ref."""

    def test_pname(self):

        test = '@test'

        path, cname, history, pname = REGEX_REF.match(test).group(
            'path', 'cname', 'history', 'pname'
        )

        self.assertEqual(pname, 'test')
        self.assertFalse(path)
        self.assertFalse(cname)
        self.assertFalse(history)

    def test_history_pname(self):

        test = '@...test'

        path, cname, history, pname = REGEX_REF.match(test).group(
            'path', 'cname', 'history', 'pname'
        )

        self.assertEqual(pname, 'test')
        self.assertEqual(history, '...')
        self.assertFalse(path)
        self.assertFalse(cname)

    def test_cname_pname(self):

        test = '@cat...test'

        path, cname, history, pname = REGEX_REF.match(test).group(
            'path', 'cname', 'history', 'pname'
        )

        self.assertEqual(pname, 'test')
        self.assertEqual(history, '..')
        self.assertEqual(cname, 'cat')
        self.assertFalse(path)

    def test_path_pname(self):

        test = '@ex\@mpl/e/..test'

        path, cname, history, pname = REGEX_REF.match(test).group(
            'path', 'cname', 'history', 'pname'
        )

        self.assertEqual(pname, 'test')
        self.assertEqual(history, '..')
        self.assertFalse(cname)
        self.assertEqual(path, 'ex\@mpl/e')

    def test_path_cname_pname(self):

        test = '@ex\@mpl/e/cat...test'

        path, cname, history, pname = REGEX_REF.match(test).group(
            'path', 'cname', 'history', 'pname'
        )

        self.assertEqual(pname, 'test')
        self.assertEqual(history, '..')
        self.assertEqual(cname, 'cat')
        self.assertEqual(path, 'ex\@mpl/e')


class RegexFormatTest(UTCase):
    """Test format expression regex."""

    def test_expr(self):

        test = '%test%'

        lang, expr = REGEX_FORMAT.search(test).group('lang', 'expr')

        self.assertFalse(lang)
        self.assertEqual(expr, 'test')

    def test_lang(self):

        test = '%py:test%'

        lang, expr = REGEX_FORMAT.search(test).group('lang', 'expr')

        self.assertEqual(lang, 'py')
        self.assertEqual(expr, 'test')


class RegexStrTest(UTCase):
    """Test str expression regex."""

    def test_expr(self):

        test = '%test%'

        lang, expr = REGEX_STR.search(test).group('lang', 'expr')

        self.assertFalse(lang)
        self.assertEqual(expr, 'test')

    def test_lang(self):

        test = '%py:test%'

        lang, expr = REGEX_STR.search(test).group('lang', 'expr')

        self.assertEqual(lang, 'py')
        self.assertEqual(expr, 'test')

    def test_pname(self):

        test = '@test'

        path, cname, history, pname = REGEX_STR.match(test).group(
            'path', 'cname', 'history', 'pname'
        )

        self.assertEqual(pname, 'test')
        self.assertFalse(path)
        self.assertFalse(cname)
        self.assertFalse(history)

    def test_history_pname(self):

        test = '@...test'

        path, cname, history, pname = REGEX_STR.match(test).group(
            'path', 'cname', 'history', 'pname'
        )

        self.assertEqual(pname, 'test')
        self.assertEqual(history, '...')
        self.assertFalse(path)
        self.assertFalse(cname)

    def test_cname_pname(self):

        test = '@cat...test'

        path, cname, history, pname = REGEX_STR.match(test).group(
            'path', 'cname', 'history', 'pname'
        )

        self.assertEqual(pname, 'test')
        self.assertEqual(history, '..')
        self.assertEqual(cname, 'cat')
        self.assertFalse(path)

    def test_path_pname(self):

        test = '@ex\@mpl/e/..test'

        path, cname, history, pname = REGEX_STR.search(test).group(
            'path', 'cname', 'history', 'pname'
        )

        self.assertEqual(pname, 'test')
        self.assertEqual(history, '..')
        self.assertFalse(cname)
        self.assertEqual(path, 'ex\@mpl/e')

    def test_path_cname_pname(self):

        test = '@ex\@mpl/e/cat...test'

        path, cname, history, pname = REGEX_STR.search(test).group(
            'path', 'cname', 'history', 'pname'
        )

        self.assertEqual(pname, 'test')
        self.assertEqual(history, '..')
        self.assertEqual(cname, 'cat')
        self.assertEqual(path, 'ex\@mpl/e')

    def test_both(self):

        test = u'@a%b%@c%js:d%@e'

        matches = REGEX_STR.finditer(test)

        values = [
            ['pname', 'a'],
            ['expr', 'b'],
            ['pname', 'c'],
            ['expr', 'd'],
            ['pname', 'e']
        ]

        for index, match in enumerate(matches):
            groupdict = match.groupdict()
            value = values[index]
            self.assertEqual(groupdict[value[0]], value[1])

    def test_wrong_both(self):

        test = '\%@a%b%\\@k@c%js:d%@e\@\\'

        matches = REGEX_STR.finditer(test)

        values = [
            ['antislash', '%'],
            ['pname', 'a'],
            ['expr', 'b'],
            ['antislash', '@'],
            ['pname', 'c'],
            ['expr', 'd'],
            ['pname', 'e'],
            ['antislash', '@'],
            ['antislash', '\\'],
        ]

        for index, match in enumerate(matches):
            groupdict = match.groupdict()
            value = values[index]
            self.assertEqual(groupdict[value[0]], value[1])


class ExprTest(UTCase):
    """Test full expression regex."""

    def test_expr(self):

        test = '=test'

        lang, expr = REGEX_EXPR.match(test).group('lang', 'expr')

        self.assertFalse(lang)
        self.assertEqual(expr, 'test')

    def test_lang(self):

        test = '=py:test'

        lang, expr = REGEX_EXPR.match(test).group('lang', 'expr')

        self.assertEqual(lang, 'py')
        self.assertEqual(expr, 'test')


class RefTest(UTCase):
    """Test the _ref function."""

    def setUp(self):

        self.pname = 'test'

        self.count = 5

        self.conf = Configuration()

        for i in range(self.count):
            cat = category(str(i), Parameter(name=self.pname, value=i))
            self.conf += cat

    def test_error(self):

        self.assertRaises(ParserError, _ref, pname=self.pname)

    def test_pname(self):

        val = _ref(pname=self.pname, conf=self.conf)

        self.assertEqual(self.count - 1, val.value)

    def test_cname(self):

        val = _ref(pname=self.pname, conf=self.conf, cname=str(self.count - 2))

        self.assertEqual(val.value, self.count - 2)

    def test_history(self):

        val = _ref(pname=self.pname, history=0, conf=self.conf)

        self.assertEqual(val.value, self.count - 1)

        val = _ref(pname=self.pname, history=1, conf=self.conf)

        self.assertEqual(val.value, self.count - 2)

    def test_history_cname(self):

        val = _ref(pname=self.pname, history=0, conf=self.conf, cname=str(self.count - 2))

        self.assertEqual(val.value, self.count - 2)

        val = _ref(pname=self.pname, history=1, conf=self.conf, cname=str(self.count - 2))

        self.assertEqual(val.value, self.count - 3)


class StrParserTest(UTCase):

    def test_empty(self):

        value = _strparser(svalue='')

        self.assertEqual(value, '')

    def test_bool(self):

        val = _strparser(svalue='0', ptype=bool)

        self.assertIs(val, False)

        val = _strparser(svalue='1', ptype=bool)

        self.assertIs(val, True)

        val = _strparser(svalue='true', ptype=bool)

        self.assertIs(val, True)

        val = _strparser(svalue='True', ptype=bool)

        self.assertIs(val, True)

    def test_list(self):

        val = _strparser(svalue='1', ptype=list)

        self.assertEqual(val, ['1'])

        val = _strparser(svalue='', ptype=list)

        self.assertFalse(val)

        val = _strparser(svalue='1, 2, 3', ptype=list)

        self.assertEqual(val, ['1', '2', '3'])

    def test_format(self):

        conf = configuration(category('', Parameter('se', value='es')))

        svalue = 't%"es"%t'

        val = _strparser(svalue=svalue, conf=conf, scope=None)

        self.assertEqual(val, 'test')

    def test_format_expr(self):

        conf = configuration(category('', Parameter('se', value='es')))

        svalue = '%"t"%@se%"t"%'

        val = _strparser(svalue=svalue, conf=conf, scope=None)

        self.assertEqual(val, 'test')

    def test_wrong_format_expr(self):

        conf = configuration(category('', Parameter('se', value='es')))

        svalue = '\@e%"t"%\%@se%"t"%\\'

        val = _strparser(svalue=svalue, conf=conf, scope=None)

        self.assertEqual(val, '@et%est\\')


class ConfigurationTest(UTCase):
    """Base class of test which uses a local configuration."""

    def setUp(self):

        self.count = 5

        self.cnames = [None] * self.count
        self.pname = 'param'
        self.pvalues = [None] * self.count

        self.conf = Configuration()

        for i in range(self.count):
            self.cnames[i] = 'c{0}'.format(i)
            self.pvalues[i] = i + 1
            cat = category(
                self.cnames[i],
                Parameter('param', value=self.pvalues[i])
            )
            self.conf += cat


class SerializerTest(ConfigurationTest):
    """Test the function serializer."""

    def test_str(self):
        """Test to serialize a string."""

        value = 'test'
        serialized = serialize(value)

        self.assertEqual(value, serialized)

    def test_none(self):
        """Test to serialize None."""

        serialized = serialize(None)

        self.assertIsNone(serialized)

    def test_other(self):
        """Test to serialize other."""

        types = [int, float, complex, dict, list, set]

        for _type in types:

            value = _type()

            serialized = serialize(value)

            self.assertEqual(serialized, '=py:{0}'.format(value))


class ParseTest(ConfigurationTest):
    """Test the parse function."""

    def test_default(self):
        """Test default params."""

        value = parse(svalue='=2')

        self.assertEqual(value, 2)

    def test_cname(self):
        """Test with cname."""

        value = parse(svalue='2')

        self.assertEqual(value, '2')

    def test_nocname(self):
        """Test when category name does not exist."""

        value = parse(svalue='t%"es"%t')

        self.assertEqual(value, 'test')

    def test_nopname(self):
        """Test when parameter name does not exist."""

        value = parse(svalue='="test"')

        self.assertEqual(value, 'test')

    def test_expr_ref(self):

        pname = 'test'

        conf = configuration(category('', Parameter('test', value='ify')))

        value = parse(svalue='="test" + @test', conf=conf)

        self.assertEqual(value, 'testify')

    def test_expr_wrong(self):

        pname = 'test'

        conf = configuration(category('', Parameter('test', value='ify')))

        value = parse(svalue='="test" + "\@fgg"', conf=conf)

        self.assertEqual(value, 'test@fgg')


if __name__ == '__main__':
    main()
