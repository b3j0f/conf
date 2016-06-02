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

The parser transforms a serializated parameter value to a parameter value,
related to parameter properties (ptype, scope, safe, etc.).

It takes in parameter:

.. csv-table:
    :header: name, description

    svalue, the serialized value
    conf, the configuration
    configurable, the configurable
    logger, a logger
    scope, dictionary of variables for expression evaluation
    ptype, final value type to check

There are two kind of values:

- simple values: string value like in most system configuration files.
- expression values: contains a dedicated programming language expression
    (python by default).

Simple value
------------

A simple value is a string. It is possible to format a dedicated programming
language expression in respecting this syntax:

*%[{lang}:]{expr}%* where:

- lang is an optional expression evaluator name (``py`` for python, ``js`` for
    javascript, etc.) Default is python.
- expr is the expression in the dedicated programming language.

.. remark::

    In order to use the character ``%`` in the expression, you just have to
    precede it by the *\* character.

Examples:

.. csv-table::

    :header: expression, result, description

    "te%'test'[:-2]%", test, 'te' + 'st' in default (python) evaluator
    "te%js:'test'.substr(2)%", test, 'te' + 'st' in javascript evaluator
    "test number %2\%2%", "test number 0", "default evaluation of 2 modulo 2"

Expression value
----------------

An expression value is an expression given in a dedicated programming language.

Therefore, the result type is not necessary a string. It depends on the
evaluated expression.

Such expression must respects this syntax:

*=[{lang}]:{expr}* where:

- expr is the expression to evaluate.
- lang is the dedicated programming language keyword (for example, ``py`` for
    python, ``js`` for javascript). Default is python.

.. remark::

    in order to use a simple expression starting with *=:*, you juste have to
    add the prefix *\*.

For example:

.. csv-table::
    :header: expression, value


    ``="example"``: string equals "example" from a python interpretor.
    ``=js:"2"``: string equals "2" from javascript interpretor.
    ``=None``: None.
    `=js:3*4``: 12 in javascript.

Reference to other parameters
-----------------------------

It is possible to reference other parameters defined in both configuration files
and configuration.

The syntax is the following:

*'@'[{confpath}/][{cat}\.]{history}{param}* where:

.. csv-table:
    :header: name, description

    confpath, "optional configuration path from where get the parameter. Default
        is current configuration path"
    cat, "optional category name. Default is current category"
    param, "referenced parameter name"
    history, "designates an old parameter from the specified/current category.
        For example:
            - '.' designates the current/specified category.
            - '..' designates the previous one parameter."
            - '...' designates the previous previous one parameter.
            - '....' etc.

For examples:

.. csv-table::
    :header: expr, description

    "@r/c.p", "parameter `p`, from the category `c` in the configuration
        resource `r` (history equals 0 from `c`)"
    "@c.p", "parameter `p` from the category `c` in the same configurable
        scope (history equals 0 from `c`)"
    "@.p", "parameter `p` from the current category. (history equals 0 from
        current category)"
    "@p", "last parameter `p` of the configurable object (history equals 0 from
        last defined category where `p` exists)"
    "@..p", "parameter `p` defined before the current category. Used frequently
        to enrich old parameter value like ``=:@..p + ['new', 'value']``"
    "@c..p", parameter `p`, defined two level before the category `c`.
"""

from __future__ import absolute_import

__all__ = ['parse', 'serialize']


from random import random

from re import compile as re_compile

from six import string_types

from collections import Iterable

from .resolver.core import DEFAULT_BESTEFFORT, DEFAULT_SAFE, DEFAULT_SCOPE

from .resolver.registry import resolve

from parser import ParserError

from json import loads


#: _ref parameter.
EVAL_REF = r'@((?P<path>([^@]|\\@)+)\/)?((?P<cname>\w+)\.)?(?P<history>\.*)(?P<pname>\w+)'

REGEX_REF = re_compile(EVAL_REF)

#: programmatic language expression.
EVAL_FORMAT = r'\%((?P<lang>\w+):)?(?P<expr>([^%]|(\\%))*[^\\])\%'

REGEX_FORMAT = re_compile(EVAL_FORMAT)

EVAL_ANTISLASH = r'(\\(?P<antislash>[@\%\\]))'

EVAL_STR = r'({0})|({1}|({2}))'.format(EVAL_ANTISLASH, EVAL_REF, EVAL_FORMAT)

REGEX_STR = re_compile(EVAL_STR)

EVAL_EXPR = r'=((?P<lang>\w+):)?(?P<expr>.*)$'  #: interpreted expression prefix

REGEX_EXPR = re_compile(EVAL_EXPR)  #: interpreted expression regex comp

EVAL_EXPR_R = r'(({0})|({1}))'.format(EVAL_ANTISLASH, EVAL_REF)

REGEX_EXPR_R = re_compile(EVAL_EXPR_R)


def serialize(expr):
    """Serialize input expr into a parsable value.

    :rtype: str"""

    result = None

    if isinstance(expr, string_types):
        result = expr

    elif expr is not None:
        result = '=py:{0}'.format(expr)

    return result


def parse(
        svalue, conf=None, configurable=None, ptype=None,
        scope=DEFAULT_SCOPE, safe=DEFAULT_SAFE, besteffort=DEFAULT_BESTEFFORT
):
    """Parser which delegates parsing to expression or format parser."""

    result = None

    if ptype is None:
        ptype = object

    compilation = REGEX_EXPR.match(svalue)

    _scope = {} if scope is None else scope.copy()

    if compilation:

        lang, expr = compilation.group('lang', 'expr')

        result = _exprparser(
            expr=expr, lang=lang, conf=conf, configurable=configurable,
            scope=_scope, safe=safe, besteffort=besteffort
        )

    else:
        result = _strparser(
            svalue=svalue, conf=conf, configurable=configurable,
            scope=_scope, safe=safe, besteffort=besteffort
        )

    # try to cast value in ptype
    if not isinstance(result, ptype):
        try:
            result = ptype(result)

        except TypeError:
            result = result

    return result


def _exprparser(
        expr, scope, lang=None, conf=None, configurable=None,
        safe=DEFAULT_SAFE, besteffort=DEFAULT_BESTEFFORT, tostr=False
):
    """In charge of parsing an expression and return a python object."""

    if scope is None:
        scope = {}

    scope.update({
        'configurable': configurable,
        'conf': conf
    })

    expr = REGEX_EXPR_R.sub(
        _refrepl(
            configurable=configurable, conf=conf, safe=safe, scope=scope,
            besteffort=besteffort
        ), expr
    )

    result = resolve(
        expr=expr, name=lang, safe=safe, scope=scope, tostr=tostr,
        besteffort=besteffort
    )

    return result


def _strparser(
        svalue, safe=DEFAULT_SAFE, ptype=None, scope=DEFAULT_SCOPE,
        configurable=None, conf=None, besteffort=DEFAULT_BESTEFFORT
):

    result = REGEX_STR.sub(
        _strrepl(
            safe=safe, scope=scope, configurable=configurable,
            conf=conf, besteffort=besteffort
        ), svalue
    )

    if ptype is None:
        ptype = str

    if not issubclass(ptype, string_types):

        if issubclass(ptype, bool):
            result = result in ('1', 'True', 'true')

        elif issubclass(ptype, dict):
            result = loads(result)

        elif issubclass(ptype, Iterable):
            if result:
                result = ptype((item.strip() for item in result.split(',')))

            else:
                result = ptype()

    return result


def _refrepl(configurable, conf, scope, safe, besteffort):

    def __repl(match, scope=scope, safe=safe, besteffort=besteffort):

        antislash, path, cname, history, pname = match.group(
            'antislash', 'path', 'cname', 'history', 'pname'
        )

        if antislash:
            result = antislash

        else:
            history = (len(history) - 1) if history else 0

            param = _ref(
                configurable=configurable, conf=conf,
                path=path, cname=cname, history=history, pname=pname
            )

            result = '_____{0}'.format(random()).replace('.', '_')

            value = param.resolve(
                configurable=configurable, conf=conf, scope=scope, safe=safe,
                besteffort=besteffort
            )

            scope[result] = value

        return result

    return __repl


def _strrepl(
        configurable, conf,
        scope=DEFAULT_SCOPE, safe=DEFAULT_SAFE, besteffort=DEFAULT_BESTEFFORT
):

    def __repl(match, scope=scope):

        antislash, lang, expr, path, cname, history, pname = match.group(
            'antislash', 'lang', 'expr', 'path', 'cname', 'history', 'pname'
        )

        if antislash:
            result = antislash

        elif expr:
            result = _exprparser(
                expr=expr, lang=lang, conf=conf, configurable=configurable,
                scope=scope, safe=safe, besteffort=besteffort, tostr=True
            )

        else:
            history = (len(history) - 1) if history else 0

            param = _ref(
                configurable=configurable, conf=conf,
                path=path, cname=cname, history=history, pname=pname
            )

            result = param.svalue

        return result

    return __repl


def _ref(
        pname, conf=None, configurable=None, cname=None, path=None, history=0
):
    """Resolve a parameter value.

    :param Configuration conf: configuration to use.
    :param str pname: parameter name.
    :param Configurable configurable: configurable.
    :param str cname: category name.
    :param str path: conf path.
    :param int history: parameter history research.
    :return: parameter.
    :raises: ParserError if conf and configurable are None.
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

    if conf is None:
        raise ParserError(
            'Wrong ref parameters. Conf and configurable are both None.'
        )

    result = conf.param(pname=pname, cname=cname, history=history)

    return result
