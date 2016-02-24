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
    vtype, final value type to check

There are two kind of values:

- simple values: string value like in most system configuration files.
- expression values: contains a dedicated programming language expression
    (python by default).

Simple value
------------

A simple value is a string. It is possible to format a dedicated programming
language expression in respecting this syntax:

*%[{lang}]:{expr}%* where:

- lang is an optional expression evaluator name (``py`` for python, ``js`` for
    javascript, etc.) Default is python.
- expr is the expression in the dedicated programming language.

.. remark::

    In order to use the character ``%`` in the expression, you just have to
    precede it by the *\* character.

Examples:

.. csv-table::

    :header: expression, result, description

    "te%:'test'[:-2]%", test, 'te' + 'st' in default (python) evaluator
    "te%js:'test'.substr(2)%", test, 'te' + 'st' in javascript evaluator
    "test number %:2\%2%", "test number 0", "default evaluation of 2 modulo 2"

Expression value
----------------

An expression value is an expression given in a dedicated programming language.

Therefore, the result type is not necessary a string. It depends on the
evaluated expression.

Such expression must respects this syntax:

*=[{lang}]:{expr}* where:

- expr is the expression to evaluate
- lang is the dedicated programming language keyword (for example, ``py`` for
    python, ``js`` for javascript). Default is python.

.. remark::

    in order to use a simple expression starting with *=:*, you juste have to
    add the prefix *\*.

For example:

.. csv-table::
    :header: expression, value


    ``=:"example"``: string equals "example" from a python interpretor.
    ``=js:"2"``: string equals "2" from javascript interpretor.
    ``=:None``: None.
    `=js:3*4``: 12 in javascript.

Reference to other parameters
-----------------------------

It is possible to reference other parameters defined in both configuration files
and configuration.

The syntax is the following:

*'@'[{confpath}|][{cat}]{history}{param}* where:

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

For examples:

.. csv-table::
    :header: expr, description

    "@r|c.p", "parameter `p`, from the category `c` in the configuration
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

__all__ = ['parse', 'EXPR_PREFIX', 'serialize']


from re import compile as re_compile

from six import string_types

from random import random

from .resolver.registry import resolve

#: ref parameter.
EVAL_REF = r'@((?P<path>([^@]|\\@)+)\/)?((?P<cat>\w+)\.)?(?P<depth>\.*)(?P<param>\w+)'

REGEX_REF = re_compile(EVAL_REF)

EVAL_FORMAT = r'%(?P<lang>\w*:)?(?P<expr>([^%]|\\%)+[^\\])%'  #: programmatic language expression.

REGEX_FORMAT = re_compile(EVAL_FORMAT)

EXPR_PREFIX = r'=(?P<lang>\w*):(?P<expr>.*)$'  #: interpreted expression prefix

EVAL_STR = r'({0})|({1})'.format(EVAL_REF, EVAL_FORMAT)

REGEX_STR = re_compile(EVAL_STR)

REGEX_PREFIX = re_compile(EXPR_PREFIX)  #: interpreted expression regex comp


def eval(expr):

    matches = REGEX_STR.finditer(expr)

    for match in matches:
        entries = match.groupdict()

        if entries['param']:
            pvalue = resolve(
                lang=entries['lang'],
                cat=entries['cat'],
                depth=len(entries['depth']),
                param=entries['param']
            )

            result = str(pvalue)

        elif entries['expr']:
            result = langeval(lang=entries['lang'], expr=entries['expr'], tostr=True)

    return result


def serialize(expr):
    """Serialize input expr into a parsable value.

    :rtype: str"""

    result = None

    if isinstance(expr, string_types):
        result = expr

    elif expr is not None:
        result = '=:{0}'.format(expr)

    return result


def parse(
        svalue, conf=None, configurable=None, vtype=object,
        scope=None, safe=True
):
    """Expression parser."""

    result = None

    compilation = REGEX_PREFIX.matches(svalue)

    if compilation:

        result = objectparser(
            svalue=svalue, compilation=compilation, conf=conf,
            configurable=configurable, vtype=vtype, scope=scope, safe=safe
        )

    else:

        result = stringparser(
            svalue=svalue, conf=conf, configurable=configurable, vtype=vtype,
            scope=scope, safe=safe
        )

    # try to cast value in vtype
    if not isinstance(result, vtype):
        try:
            result = vtype(result)

        except TypeError:
            result = result

    return result


def objectparser(
        compilation, conf=None, configurable=None, scope=None, safe=True
):

    lang, expr = compilation.groups()

    default_scope = {
        '_resolve': resolve,
        'configurable': configurable,
        'conf': conf,
        'true': True,
        'false': False,
        '_scope': scope
    }

    if scope is None:
        scope = default_scope

    else:
        scope.update(default_scope)

    result = resolve(
        expr=expr, name=lang, safe=safe, scope=scope, tostr=False
    )

    return result


def stringparser(svalue, safe=True, vtype=str, scope=None, configurable=None):

    repl = _repl(safe=safe, scope=scope, configurable=configurable, tostr=True)

    result = EVAL_REGEX.sub(repl, svalue)

    if issubclass(vtype, bool):
        result = result in ('1', 'True', 'true')

    return result


def _repl(scope, safe=True, tostr=True, conf=None, configurable=None):
    """Replace matching expression in input match with corresponding
    conf accessor."""

    def __repl(match):
        """Internal regex repl function."""

        result = None

        confpath, cname, history, pname, lang, expr = match.groups()

        if expr:
            result = resolve(
                expr=expr, name=lang, safe=safe, tostr=tostr, scope=scope
            )

            if not tostr:
                while True:
                    var = '_{0}'.format(random()).replace('.', '_')
                    if var not in scope:
                        scope[var] = result
                        result = var
                        break

        else:
            result = lookup(
                pname=pname, conf=conf, configurable=configurable, cname=cname,
                path=confpath, history=history
            )

            if tostr:
                result = str(result)

        return result

    return __repl


def lookup(
        pname, conf=None, configurable=None, cname=None, path=None, history=0
):
    """Resolve a parameter value.

    :param Configuration conf: configuration to use.
    :param str pname: parameter name.
    :param Configurable configurable: configurable.
    :param str cname: category name.
    :param str path: conf path.
    :param int history: parameter history research.
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

    result = conf.pvalue(pname=pname, cname=cname, history=history)

    return result
