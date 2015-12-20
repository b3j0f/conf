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

The parser transform a serialization parameter value to a parameter value,
related to parameter properties (_type, _globals, _locals, etc.).

It takes in parameter :

- svalue: the serialized value.
- configuration: the configuration.
- configurable: the configurable.
- logger: a logger.
- _locals and _globals respective dictionaries of local/global variables for python expressions.
- _type: final value type to check.

There are two kind of values:

- simple values: like in most system configuration files, such values are string by default.
- expression values: contains a python expression.

Simple value
-------------

Expression value
----------------

Expression values are evaluated in a safe context (without I/O functions).

For example:

- ``2``: default integer value.
- ``true``: default boolean value.
- ``test``: default string value.
- ``="test".capitalize()``: expression value which result in a string value.
- ``=3**4: expression value which result in an integer value.

expressions accept those keywords which does not exist in the python language.

- '#'{path}: get a python object given by the ``path`` value.
- '@'[://{confpath}/][{cat}.]{param}: param value from optionnally cat and confpath.

.. csv-table::
    :header: expr, description

    "@://r/c.p", "parameter p, from the category c in the configuration resource r"
    "@c.p", "parameter value from the category c in the same configurable scope"
    "@p", "last parameter value of the configurable object"
"""

from __future__ import absolute_import

__all__ = ['parse', 'ParserError', 'EXPR_PREFIX', 'serialize']


from b3j0f.utils.path import lookup
from b3j0f.utils.runtime import safe_eval

from re import compile as re_compile

from parser import ParserError

from six import string_types

WORD = r'[a-zA-Z_]\w*'

EVAL_REF = r'@(:\/\/[^\/@]+\/)?({0}\.)?({0})'.format(WORD)  #: ref parameter.

EVAL_LOOKUP = r'#({0}\.?)+'.format(WORD)  #: lookup param regex.

EVAL_REGEX = '{0}|{1}'.format(EVAL_REF, EVAL_LOOKUP)  #: all regex.

REGEX_COMP = re_compile(EVAL_REGEX)  #: final regex compiler.

EXPR_PREFIX = '='  #: expression prefix


def serialize(expr):
    """Serialize input expr into a parsable value.

    :rtype: str"""

    result = None

    if isinstance(expr, string_types):
        result = expr

    elif expr is not None:
        result = '{0}{1}'.format(EXPR_PREFIX, expr)

    return result


def parse(
        svalue, conf=None, configurable=None, _type=object,
        _locals=None, _globals=None, safe=True
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

    if svalue.startswith(EXPR_PREFIX):

        value = _exprparser(
            svalue=svalue[len(EXPR_PREFIX):], conf=conf,
            configurable=configurable, _locals=_locals, _globals=_globals
        )

    else:
        value = _simpleparser(svalue=svalue, _type=_type)

    result = value

    # try to cast value in _type
    if not isinstance(result, _type):
        try:
            result = _type(value)

        except TypeError:
            result = value

    return result


def _simpleparser(svalue, _type=str):
    """Execute a simple parsing.

    :param str svalue: serialized value to parse.
    :param type _type: expected value type.
    """

    result = svalue

    if issubclass(_type, bool):
        result = result in ('1', 'True', 'true')

    return result


def _exprparser(
        svalue, conf=None, configurable=None, _locals=None, _globals=None,
        safe=True
):
    """Parse input serialized value such as an expression."""

    result = None

    compilation = REGEX_COMP.sub(_repl, svalue)

    if compilation:

        default_locals = {
            'resolve': _resolve,
            'configurable': configurable,
            'lookup': lookup,
            'conf': conf
        }

        final_locals = _getscope(_locals, default_locals)

        default_locals = {}

        final_globals = _getscope(_globals)

        expreval = safe_eval if safe else eval

        result = expreval(compilation, final_globals, final_locals)

    return result


def _repl(match):
    """Replace matching expression in input match with corresponding
    conf accessor."""

    result = None

    confpath, cname, pname, path = match.groups()

    if path:
        result = 'lookup(path=\'{0}\')'.format(path)

    else:
        params = 'pname=\'{0}\''.format(pname)

        if confpath:
            confpath = confpath[3:-1]
            params += ', path=\'{0}\''.format(confpath)

        if cname:
            cname = cname[:-1]
            params += ', cname=\'{0}\''.format(cname)

        conf = 'configurable=configurable, conf=conf'
        result = 'resolve({0}, {1})'.format(conf, params)

    return result


def _resolve(pname, conf=None, configurable=None, cname=None, path=None):
    """Resolve a foreign parameter value.

    :param Configuration conf: configuration to use.
    :param str pname: parameter name.
    :param Configurable configurable: configurable.
    :param str cname: category name.
    :param str path: conf path.
    :return: parameter
    """

    result = None

    if configurable is not None:
        kwargs = {}
        if conf is not None:
            kwargs['conf'] = conf
        if path is not None:
            kwargs['paths'] = path

        if conf is None:
            conf = configurable.getconf(**kwargs)

    result = conf.pvalue(pname=pname, cname=cname)

    return result


def _getscope(*scopes):
    """Construct a scope from less specific to more specific scopes."""

    result = {}

    for scope in scopes:
        if scope is not None:
            result.update(scope)

    return result
