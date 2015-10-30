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

"""Parameter parser module.

A parser is able to transform a serialized parameter value to a python object.

A parser is a callable object which takes in parameter :

- value: the serialized value.
- conf: the configuration.
- logger: a logger.
"""

__all__ = [
    'boolparser', 'pathparser', 'jsonparser', 'dictparser', 'arrayparser',
    'exprparser'
]


from b3j0f.utils.path import lookup
from b3j0f.utils.runtime import safe_eval

from json import loads as jsonloads

from re import compile as re_compile

from .parameter import Parameter
from .configuration import Configuration


def simpleparser(function):
    """Parser to use with a function which takes in parameter only one param.

    For example, simpleparser(int) returns a parser of integer.
    """

    def parse(value, *args, **kwargs):

        return function(value)

    return parse


intparser = simpleparser(int)  #: Integer value parser.
floatparser = simpleparser(float)  #: Float value parser.
complexparser = simpleparser(complex)  #: complex value parser.
strparser = simpleparser(str)  #: str value parser.


def boolparser(value, *args, **kwargs):
    """Boolean value parser.

    :param str value: value to parse.
    :return: True if value in [True, true, 1]. False Otherwise.
    :rtype: bool
    """

    return value == 'True' or value == 'true' or value == '1'


def pathparser(value, *args, **kwargs):
    """Python class path value parser.

    :param str value: python class path to parse.
    :return: lookup(value).
    """

    return lookup(value)


def jsonparser(value, *args, **kwargs):
    """Get a data from a json data format.

    :param str value: json format to parse.
    :return: data.
    :rtype: str, list, dict, int, float or bool
    """

    return jsonloads(value, *args, **kwargs)


def _typedjsonparser(value, cls, *args, **kwargs):
    """Private static method which uses the json method and check if result
    inherits from the cls. Otherwise, raise an error.

    :param str value: value to parse in a json format.
    :param type cls: expected result class.
    :return: parsed value.
    :rtype: cls
    """

    result = jsonparser(value, *args, **kwargs)

    if not isinstance(result, cls):
        raise Parameter.Error(
            'Wrong type: {0}. {1} expected.'.format(value, cls)
        )

    return result


def dictparser(value, *args, **kwargs):
    """Get a dict from a dict json format.

    :param str value: dictionary json format to parse.
    :return: parsed dictionary.
    :rtype: dict
    :raises: Parameter.Error if value is not a dict json format.
    """

    return _typedjsonparser(value, dict, *args, **kwargs)


def arrayparser(value, *args, **kwargs):
    """Get an array from:

    - an array json format.
    - a list of item name separated by commas.

    :param str value: list of items to parse. The format must be of

        - array json type.
        - named item separated by commas.

    :return: parsed array.
    :rtype: list
    :raises: Parameter.Error if value is not a list json format.
    """

    if value[0] == '[':
        result = _typedjsonparser(value, list, *args, **kwargs)

    else:
        result = list(value.split(','))

    return result

EVAL_REGEX = r'((?<=\$)[a-zA-Z_]\w*)(\.[a-zA-Z_]\w*)?'  #: eval regex.
EVAL_COMPILED_REGEX = re_compile(EVAL_REGEX)  #: eval compiled regex.


def exprparser(value, conf, *args, **kwargs):
    """Expression parser.

    Evaluate safely input value.

    Value is a lambda body expression evaluated in a safely scope (only builtin
    is loaded) where configuration categories/parameters are prefixed by the
    character '$'.

    For example, ``$cat.param`` designates the value of the category named
    ``cat`` and the parameter named ``param``. And ``$param`` designates
    the final value of the parameter named ``param``.
    """

    result = None

    def repl(match):
        """Replace matching expressin in match with corresponding conf accessor
        ."""

        result = match

        if match[1]:
            result = 'conf[{0}][{1}].value'.format(
                Configuration.VALUES, match[0]
            )

        else:
            result = 'conf[{0}][{1}].value'.format(*match)

        return result

    compilation = EVAL_COMPILED_REGEX.sub(repl, value)

    if compilation:

        _locals = {'conf': conf}

        result = safe_eval(compilation, None, _locals)

    return result
