# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2015 Jonathan Labéjof <jonathan.labejof@gmail.com>
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

"""Parameter parser module.

A parser is able to transform a serialized parameter value to a python object.

A parser is a callable object which takes in parameter :

- svalue: the serialized value.
- configuration: the configuration.
- configurable: the configurable.
- logger: a logger.
- _locals and _globals respective dictionaries of local/global variables.
- _type: final value type to check.
"""

__all__ = ['boolparser', 'getexprparser', 'exprparser', 'ParserError']


from b3j0f.utils.path import lookup
from b3j0f.utils.runtime import safe_eval

from re import compile as re_compile


class ParserError(Exception):
    """Handle parser errors."""


EVAL_PARAM = r'\$([a-zA-Z_]\w*)(\.[a-zA-Z_]\w*)+?'  #: local param regex.
EVAL_FOREIGN = r'\@([.^\/]+)\/([a-zA-Z_]\w*)\.([a-zA-Z_]\w*)'  #: foreign param re.
EVAL_LOOKUP = r'\#([a-zA-Z_]\w*\.?)+'  #: lookup param regex.

REGEX = '({0})|({1})|({2})'.format(EVAL_PARAM, EVAL_LOOKUP, EVAL_FOREIGN)
COMPILED_REGEX = re_compile(REGEX)


def getexprparser(_globals=None, _locals=None):
    """Generate an expression parser from input parameters."""

    def _exprparser(
            svalue, configuration=None, configurable=None, _type=object,
            _locals=None, _globals=None, __locals=_locals, __globals=_globals,
            *args, **kwargs
    ):
        """Expression parser.

        Evaluate safely input svalue.

        Value is a lambda body expression evaluated in a safely scope (only
        builtin is loaded) where configuration categories/parameters are
        prefixed by the character '$'.

        For example, ``$cat.param`` designates the svalue of the category named
        ``cat`` and the parameter named ``param``. And ``$param`` designates
        the final svalue of the parameter named ``param``.
        """

        result = None

        compilation = COMPILED_REGEX.sub(repl, svalue)

        if compilation:

            if _locals is None:
                _locals = {}

            if __locals is not None:
                _locals.update(__locals)

            _locals.update(
                {
                    'resolve': _resolve,
                    'configurable': configurable,
                    'lookup': lookup,
                    'configuration': configuration
                }
            )

            if _globals is None:
                _globals = {}

            if __globals is not None:
                _globals.update(__globals)

            result = safe_eval(compilation, _globals, _locals)

            if not isinstance(result, _type):

                # try to convert to _type
                try:
                    result = _type(result)

                except Exception:
                    pass

                if not isinstance(result, _type):

                    raise ParserError(
                        'Wrong svalue {0}. {1} expected.'.format(svalue, _type)
                    )

        return result

    return _exprparser


def repl(match):
    """Replace matching expression in input match with corresponding
    conf accessor."""

    result = match

    if match[0] == '`':

        result = 'lookup(path={0})'.format(match[1:])

    elif match[0] == '@':

        result = '_resolve(match={0}, configurable=configurable)'.format(
            match[1:]
        )

    elif match[1]:
        result = 'configuration[{0}][{1}].value'.format(*match)

    else:
        result = 'configuration.getvparam({0}).value'.format(match[0])

    return result


def _resolve(match, configurable):
    """Resolve a foreign parameter value."""

    result = None

    path, cat, param = match

    conf = configurable.get_conf(paths=path)

    category = conf.get(cat)

    if category is not None:
        parameter = category.get(param)

        if parameter is not None:
            result = parameter.value

    if result is None:
        raise ParserError(
            'Foreign value ({0}) does not exist.'.format(match)
        )

    return result


exprparser = getexprparser()  #: default expr parser.


def boolparser(*args, **kwargs):
    """Boolean value parser.

    :param str svalue: serialized value to parse.
    :return: True if svalue in [True, true, 1]. False Otherwise.
    :rtype: bool
    """

    _locals = {
        'true': True
    }

    return exprparser(_type=bool, _locals=_locals, *args, **kwargs)
