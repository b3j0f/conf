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

"""Parameter definition objects."""

from __future__ import absolute_import

__all__ = ['Parameter', 'PType']

from .base import ModelElement
from ..parser.core import parse, serialize

from parser import ParserError

from six import string_types, reraise

from re import compile as re_compile

from collections import Iterable

from ..parser.resolver.core import (
    DEFAULT_SAFE, DEFAULT_BESTEFFORT, DEFAULT_SCOPE
)


class PType(object):
    """Dedicated to embed a specific type such as a parameter type in order to
    instanciate easily this embedded type from a parameter serialized value.

    Instanciation depends on type of serialiazed value (by order):

    - str: first arg to this ptype.
    - dict: it is given such as a kwargs to this ptype.
    - iterable: it is given such as an args to this ptype.
    - object: it is given such as the only one argument to this ptype.
    """

    __slots__ = ('ptype')

    def __init__(self, ptype, *args, **kwargs):

        super(PType, self).__init__(*args, **kwargs)

        self.ptype = ptype

    def __instancecheck__(self, instance):
        """Check instance such as this instance or self ptype instance."""

        return isinstance(instance, (PType, self.ptype))

    def __subclasscheck__(self, subclass):
        """Check subclass such as this subclass or self ptype subclass."""

        return issubclass(subclass, (PType, self.ptype))

    def __call__(self, svalue):
        """Instantiate a new instance of this ptype related to input value.

        :param ssvalue: Instanciation depends on type of serialiazed value
            (by order):

        - dict: it is given such as a kwargs to this ptype.
        - iterable: it is given such as an args to this ptype.
        - object: it is given such as the only one argument to this ptype."""

        result = None

        args, kwargs = [], {}

        if isinstance(svalue, string_types) or not isinstance(svalue, Iterable):
            args = [svalue]

        elif isinstance(svalue, dict):
            kwargs = svalue

        else:
            args = svalue

        try:
            result = self.ptype(*args, **kwargs)

        except TypeError:
            msg = 'Wrong value ({0}) with ({1}).'.format(svalue, self.ptype)
            reraise(ParserError, ParserError(msg))

        return result


class Bool(PType):
    """Parameter type dedicated to boolean values."""

    def __init__(self, *args, **kwargs):

        super(Bool, self).__init__(ptype=bool, *args, **kwargs)

    def __call__(self, svalue):

        return svalue in ('true', 'True', '1')


class Array(PType):
    """Parameter type dedicated to array value."""

    def __init__(self, *args, **kwargs):

        super(Array, self).__init__(ptype=Iterable, *args, **kwargs)

    def __call__(self, svalue):

        return list(item.trim() for item in svalue.split(','))


class Parameter(ModelElement):
    """Parameter identified among a category by its name.

    Provide a value (None by default) and a parser (str by default).

    Properties are:

    - name: parameter name. If regex, drivers will generated as many parameters
        as they exist in the configuration resource with this properties (
        value, conf, parser, etc.).
    - value: parameter value. None if error is not None.
    - error: parameter error encountered while attempting to set values.
    - parser: parameter value parser from configuration resources.
    - conf: parameter configuration if not None. If not None, the value must be
        a callable beceause the conf is used such as a kwargs.
    - local: distinguish local parameters from those found in configuration
        resources.
    """

    __slots__ = (
        '_name', 'ptype', 'parser', '_svalue', '_value', '_error', 'conf',
        'local', 'scope', 'configurable', 'serializer', 'besteffort', 'safe'
    ) + ModelElement.__slots__

    class Error(Exception):
        """Handle Parameter errors."""

    CONF_SUFFIX = '::conf'  #: parameter configuration name.

    PARAM_NAME_REGEX = r'[a-zA-Z_]\w*'  #: simple name validation.
    #: simple name regex compiler.
    _PARAM_NAME_COMPILER_MATCHER = re_compile(PARAM_NAME_REGEX).match

    DEFAULT_NAME = re_compile('.*')
    DEFAULT_PTYPE = object  #: default ptype.
    DEFAULT_LOCAL = True  #: default local value.

    def __init__(
            self, name=DEFAULT_NAME, value=None, ptype=DEFAULT_PTYPE,
            parser=parse, serializer=serialize, svalue=None,
            conf=None, configurable=None,
            local=DEFAULT_LOCAL, scope=DEFAULT_SCOPE, safe=DEFAULT_SAFE,
            besteffort=DEFAULT_BESTEFFORT,
            *args, **kwargs
    ):
        """
        :param name: depends on type:
            - str: unique by category.
            - regex: designates a group of parameters with a matching name and
                common properties (parser, value, conf, etc.).

            Default is the regex ``.*``.
        :param value: param value. None if not given.
        :param type ptype: parameter value type.
        :param callable parser: param value deserializer which takes in param a
            str. Default is the expression parser.
        :param callable serializer: param serializer which takes in param an
            object and retuns a string. Default is the expression serializer.
        :param str svalue: serialized value.
        :param dict conf: parameter configuration used to init the parameter
            value if not None. In this case, the parameter value must be
            callable.
        :param Configurable configurable: specific configuable.
        :param bool local: distinguish local parameters from those defined
            outside the configuration while updating the embedding conf.
        :param dict scope: dictionary of elements to add in the serialized
            value evaluation.
        """

        super(Parameter, self).__init__(*args, **kwargs)

        # init protected attributes
        self._name = None
        self._value = value
        self._error = None
        self._svalue = svalue

        # init public attributes
        self.parser = parser
        self.serializer = serializer
        self.ptype = ptype
        self.conf = conf
        self.configurable = configurable
        self.local = local
        self.scope = scope
        self.besteffort = besteffort
        self.safe = safe

        # init setters
        self.name = name
        #self.svalue = svalue
        #self.value = value

    def __eq__(self, other):
        """
        :return: True iif other is a parameter and has the same name than
            this.
        :rtype: bool"""

        result = isinstance(other, Parameter)

        if result:
            if isinstance(self.name, string_types):
                if isinstance(other.name, string_types):
                    result = self.name == other.name

                else:
                    result = other.name.match(self.name)

            else:
                if isinstance(other.name, string_types):
                    result = self.name.match(other.name)

                else:
                    result = self.name.pattern == other.name.pattern

        return result

    def __hash__(self):
        """Get parameter hash value.

        :return:hash(self.name)+hash(Parameter).
        :rtype: int"""

        return hash(self.name) + hash(Parameter)

    @property
    def error(self):
        """Get encountered error.

        :rtype: Exception"""

        return self._error

    @property
    def name(self):
        """Get parameter name.

        :return: this name.
        :rtype: str
        """

        return self._name

    @name.setter
    def name(self, value):
        """Set parameter name.

        :param str value: name value.
        """

        if isinstance(value, string_types):

            match = Parameter._PARAM_NAME_COMPILER_MATCHER(value)

            if match is None or match.group() != value:
                value = re_compile(value)

        self._name = value

    @property
    def conf_name(self):
        """Get this configuration name.

        :return: {self.name}{CONF_SUFFIX}.
        :rtype: str
        """

        return '{0}{1}'.format(self.name, Parameter.CONF_SUFFIX)

    @property
    def svalue(self):
        """Get serialized value.

        :rtype: str
        """

        result = self._svalue

        if result is None:  # try to get svalue from value if svalue is None

            try:
                value = self.value

            except Parameter.Error:
                pass

            else:
                result = self._svalue = self.serializer(value)

        return result

    @svalue.setter
    def svalue(self, value):
        """Change of serialized value.

        Nonify this value as well.

        :param str value: serialized value to use.
        """

        if value is not None:  # if value is not None
            self.clean()  # clean this parameter

        self._svalue = value  # set svalue

    def resolve(
            self,
            configurable=None, conf=None, scope=None, ptype=None,
            parser=None, error=True, svalue=None,
            safe=None, besteffort=None
    ):
        """Resolve this parameter value related to a configurable and a
        configuration.

        Save error in this attribute `error` in case of failure.

        :param str svalue: serialized value too resolve. Default is this svalue.
        :param Configurable configurable: configurable to use for foreign
            parameter resolution.
        :param Configuration conf: configuration to use for
            cross-value resolution.
        :param dict scope: variables to use for local expression evaluation.
        :param type ptype: return type. Default is this ptype.
        :param parser: specific parser to use. Default this parser.
        :param bool error: raise an error if True (False by default).
        :param bool safe: if True (default) resolve without builtins functions.
        :param bool besteffort: best effort flag. Default is this besteffort.
        :return: newly resolved value.
        :raises: Parameter.Error for any raised exception.
        """

        result = self._value

        # if cached value is None and serialiazed value exists
        if self._value is None and self._svalue is not None:

            self._error = None  # nonify error.

            if ptype is None:
                ptype = self.ptype

            if parser is None:  # init parser
                parser = self.parser

            if svalue is None:
                svalue = self._svalue

            if conf is None:  # init conf
                conf = self.conf

            if configurable is None:  # init configurable
                configurable = self.configurable

            if scope is None:
                scope = self.scope

            else:
                scope, selfscope = self.scope.copy(), scope
                scope.update(selfscope)

            if safe is None:
                safe = self.safe

            if besteffort is None:
                besteffort = self.besteffort

            # parse value if str and if parser exists
            try:
                result = self._value = parser(
                    svalue=svalue, conf=conf,
                    configurable=configurable, ptype=ptype,
                    scope=scope, safe=safe, besteffort=besteffort
                )

            except Exception as ex:

                self._error = ex
                if error:
                    msg = 'Impossible to parse value ({0}) with {1}.'
                    msg = msg.format(self._svalue, self.parser)
                    reraise(Parameter.Error, Parameter.Error(msg))

        return result

    @property
    def value(self):
        """Get parameter value.

        If this cached value is None and this serialized value is not None,
        calculate the new value from the serialized one.

        :return: parameter value.
        :raises: TypeError if serialized value is not an instance of self ptype
            . ParserError if parsing step raised an error.
        """

        result = self._value

        if result is None and self._svalue is not None:

            try:
                result = self._value = self.resolve()

            except Exception:
                reraise(
                    Parameter.Error,
                    Parameter.Error('Call the method "resolve" first.')
                )

        return result

    @value.setter
    def value(self, value):
        """Change of parameter value.

        If an error occured, it is stored in this error attribute.

        :param value: new value to use. If input value is not an instance of
            self.ptype, self error
        :raises: TypeError if input value is not an instance of self ptype.
        """

        if value is None or (
                self.ptype is not None and isinstance(value, self.ptype)
        ):
            self._value = value

        else:
            # raise wrong type error
            error = TypeError(
                'Wrong value type of ({0}). {1} expected.'.format(
                    value, self.ptype
                )
            )
            self._error = error
            raise error

    def copy(self, cleaned=False, *args, **kwargs):
        """Get a copy of the parameter with specified name and new value if
        cleaned.

        :param str name: new parameter name.
        :param bool cleaned: clean the value.
        :return: new parameter.
        """

        props = (
            'name', 'parser', 'local', 'ptype', 'conf', 'scope', 'besteffort'
        )
        for prop in props:
            kwargs.setdefault(prop, getattr(self, prop))

        if not cleaned:  # add value and svalue if not cleaned
            kwargs.setdefault('value', self._value)
            kwargs.setdefault('svalue', self._svalue)

        result = super(Parameter, self).copy(cleaned=cleaned, *args, **kwargs)

        return result

    def clean(self):
        """Clean this param in removing values."""

        self._value = None
        self._svalue = None
        self._error = None
