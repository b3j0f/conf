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
- ``:="test".capitalize()``: expression value which result in a string value.
- ``:=3**4: expression value which result in an integer value.

expression values accept three keywords which does not exist in the python language.

- '#'{path}: get a python object given by the ``path`` value.
- '@'({r}'/')?({c}?'.')?{p}: use a parameter value specified in the same scope than the input configuration, where ``r``, ``c`` and ``p`` designate respectively the resource, the category and the parameter to retrieve.

.. csv-table::
    :header: expr, description

    - @r/c.p, "parameter p, from the category c in the configuration resource r"
    - @c.p, "parameter value from the category c in the same configurable scope"
    - @.p, "parameter value from the current category"
    - @p, "last parameter value of the configurable object"
"""

__all__ = ['parser', 'ParserError', 'getscope']


from b3j0f.utils.path import lookup
from b3j0f.utils.runtime import safe_eval

from re import compile as re_compile


class ParserError(Exception):
    """Handle parser errors."""


REF_PREFIX = '@'
LOOKUP_PREFIX = '#'

#: ref parameter.
EVAL_REF = r'{0}([.^\/]+\/){1}?([a-zA-Z_]\w*){1}?(\.)?([a-zA-Z_]\w*)'
EVAL_REF = EVAL_REF.format(REF_PREFIX, '{1}')
#: lookup param regex.
EVAL_LOOKUP = r'{0}([a-zA-Z_]\w*\.?)+'.format(LOOKUP_PREFIX)

REGEX = r'({0})|({1})'.format(EVAL_LOOKUP, EVAL_REF)
COMPILED_REGEX = re_compile(REGEX)

EXPR_PREFIX = ':='  #: expression prefix


def parser(
        svalue, configuration=None, configurable=None, _type=object,
        _locals=None, _globals=None, *args, **kwargs
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
            svalue=svalue[len(EXPR_PREFIX):], configuration=configuration,
            configurable=configurable, _locals=_locals, _globals=_globals
        )

    else:
        value = _simpleparser(svalue=svalue, _type=_type)

    result = value

    # try to cast value in _type
    if not isinstance(result, _type):
        try:
            result = _type(svalue)

        except TypeError:
            result = value

    return result


def _simpleparser(svalue, _type):
    """Execute a simple parsing.

    :param str svalue: serialized value to parse.
    :param type _type: expected value type.
    """

    result = svalue

    if issubclass(_type, bool):
        result = result in ('1', 'True', 'true')

    return result


def _exprparser(
        svalue, configuration=None, configurable=None,
        _locals=None, _globals=None
):
    """Parse input serialized value such as an expression."""

    compilation = COMPILED_REGEX.sub(_repl, svalue)

    if compilation:

        default_locals = {
            'resolve': _resolve,
            'configurable': configurable,
            'lookup': lookup,
            'configuration': configuration
        }

        final_locals = getscope(_locals, default_locals)

        default_locals = {}

        final_globals = getscope(_globals)

        result = safe_eval(compilation, final_globals, final_locals)

    return result


def _repl(match):
    """Replace matching expression in input match with corresponding
    conf accessor."""

    result = match

    if match[0]:  # is a lookup ?

        result = 'lookup(path=\'{0}\')'.format(match[1:])

    else:  # is a reference

        path, cname, rel, pname = match[1]  # get path, cname and pname

        params = 'path=\'{0}\', cname=\'{1}\', pname=\'{2}\', rel={3}'.format(
            path, cname, pname, rel
        )
        conf = 'configurable=configurable, configuration=configuration'
        result = '_resolve({0}, {1}, {2})'.format(conf, params, rel)

    return result


def _resolve(path, cname, pname, rel, configurable, configuration):
    """Resolve a foreign parameter value."""

    result = None

    conf = configurable.get_conf(paths=path)

    if cname is None:
        parameter = configuration.getparam(pname)

    else:

        category = conf.get(cname)

        if category is not None:
            parameter = category.get(pname)

    if parameter is not None:
        result = parameter.value

    if result is None:
        raise ParserError(
            'Foreign value ({0}) does not exist.'.format(match)
        )

    return result


def getscope(*scopes):
    """Construct a scope from less specific to more specific scopes."""

    result = {}

    for scope in scopes:
        if scope is not None:
            result.update(scope)

    return result
