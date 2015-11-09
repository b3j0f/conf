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

"""Configuration definition objects."""

__all__ = ['Parameter']


from .base import ModelElement

from six import string_types, reraise

from re import compile as re_compile

from .parser import parser, getscope


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
    - critical: if True (False by default), set a configurable property
    - local: distinguish local parameters from those found in configuration
        resources.
    - asitem: distinguish parameters from those in a ParamList.
    """

    __slots__ = (
        '_name', 'vtype', 'parser', '_svalue', '_value', '_error', 'conf',
        'critical', 'local', 'asitem', 'name', 'value', '_globals', '_locals',
        'svalue'
    ) + ModelElement.__slots__

    CONF_SUFFIX = '::conf'  #: parameter configuration name.

    PARAM_NAME_REGEX = r'[a-zA-Z_]\w*'  #: simple name validation.
    #: simple name regex compiler.
    _PARAM_NAME_COMPILER = re_compile(PARAM_NAME_REGEX)

    class Error(Exception):
        """Handle Parameter errors."""

    def __init__(
            self, name, vtype=object, svalue=None, parser=parser,
            value=None, conf=None, critical=False, local=True, asitem=None,
            _globals=None, _locals=None,
            *args, **kwargs
    ):
        """
        :param name: depends on type:
            - str: unique by category.
            - regex: designates a group of parameters with a matching name and
                common properties (parser, value, conf, etc.).
        :param type vtype: parameter value type.
        :param callable parser: param test deserializer which takes in param
            a str. Default is exprparser.
        :param str svalue: serialized value.
        :param value: param value. None if not given.
        :param dict conf: parameter configuration used to init the parameter
            value if not None. In this case, the parameter value must be
            callable.
        :param bool critical: True if this parameter is critical. A critical
            parameter can require to restart a component for example.
        :param bool local: distinguish local parameters from those found in
            configuration resources.
        :param Category asitem: distinguish parameters from those in a
            ParamList.
        """

        super(Parameter, self).__init__()

        # init private attributes
        self._name = None
        self._value = None
        self._error = None
        self._svalue = None

        # init public attributes
        self.parser = parser
        self.name = name
        self.vtype = vtype
        self.conf = conf
        self.critical = critical
        self.local = local
        self.asitem = asitem
        self.svalue = svalue
        self.value = value
        self._globals = _globals
        self._locals = _locals

    def __eq__(self, other):

        return isinstance(other, Parameter) and other.name == self.name

    def __hash__(self):

        return hash(self.name)

    def __repr__(self):

        return 'Parameter({0}, {1}, {2})'.format(
            self.name, self.value, self.parser
        )

    @property
    def error(self):
        """Get encountered error."""

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

            if not Parameter._PARAM_NAME_COMPILER.match(value):
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

        try:
            value = self.value

        except Parameter.Error:
            pass

        else:
            if isinstance(value, string_types):
                result = '"{0}"'.format(self._svalue)

        return result

    @svalue.setter
    def svalue(self, value):
        """Change of serialized value.

        Nonify this value as well.

        :param str value: serialized value to use.
        """

        self._value = None  # nonify this value
        self._error = None  # nonify this error
        self._svalue = value  # set svalue

    def resolve(
            self,
            configurable=None, configuration=None, _locals=None, _globals=None,
            parser=None
    ):
        """Resolve this parameter value related to a configurable and a
        configuration.

        :param Configurable configurable: configurable to use for foreign
            parameter resolution.
        :param Configuration configuration: configuration to use for
            cross-value resolution.
        :param dict _locals: local variable to use for local python expression
            resolution.
        :param dict _globals: global variable to use for local python
            expression resolution.
        :param parser: specific parser to use. Default this parser.
        :return: newly resolved value.
        :raises: Parameter.Error for any raised exception.
        """

        result = self._value

        # if cached value is None and serialiazed value exists
        if self._value is None and self._svalue is not None:

            self._error = None  # nonify error.

            if parser is None:
                parser = self.parser

            if parser is None:
                result = self.value = self._svalue

            else:

                _locals = getscope(self._locals, _locals)
                _globals = getscope(self._globals, _globals)

                # parse value if str and if parser exists
                try:
                    finalvalue = parser(
                        svalue=self._svalue, configuration=configuration,
                        configurable=configurable, _type=self.vtype,
                        _locals=_locals, _globals=_globals
                    )

                except Exception as ex:
                    self._error = ex
                    msg = 'Impossible to parse value "{0}" with {1}.'.format(
                        self._svalue, self.parser
                    )
                    reraise(Parameter.Error, Parameter.Error(msg))

                else:
                    # try to apply conf
                    if finalvalue is None or self.conf is None:
                        result = self.value = finalvalue

                    else:  # apply conf
                        try:
                            result = self.value = finalvalue(**self.conf)

                        except Exception as ex:
                            self._error = ex
                            msg = 'while calling param conf {0} on {1}.'.format(
                                self.conf, finalvalue
                            )
                            reraise(Parameter.Error, Parameter.Error(msg))

        return result

    @property
    def value(self):
        """Get parameter value.

        If this cached value is None and this serialized value is not None,
        calculate the new value from the serialized one.

        :return: parameter value.
        :raises: TypeError if serialized value is not an instance of self vtype
            . ParserError if parsing step raised an error.
        """

        result = self._value

        if self._value is None and self._svalue is not None:

            try:
                result = self.resolve()

            except Exception as ex:

                raise Parameter.Error(
                    'Call the method "resolve" first.'
                ).with_traceback(ex.__traceback__)

        return result

    @value.setter
    def value(self, value):
        """Change of parameter value.

        If an error occured, it is stored in this error attribute.

        :param value: new value to use. If input value is not an instance of
            self.vtype, self error
        :raises: TypeError if input value is not an instance of self vtype.
        """

        if value is None or (
                self.vtype is not None and isinstance(value, self.vtype)
        ):

            self._value = value

        else:
            # raise wrong type error
            error = TypeError(
                'Wrong value type of {0}. {1} expected.'.format(
                    value, self.vtype
                )
            )
            self._error = error
            raise error

    def copy(self, name=None, cleaned=False):
        """Get a copy of the parameter with specified name and new value if
        cleaned.

        :param str name: new parameter name.
        :param bool cleaned: clean the value.
        :return: new parameter.
        """

        if name is None:
            name = self.name

        kwargs = {
            'name': name,
            'parser': self.parser,
            'local': self.local,
            'critical': self.critical,
            'vtype': self.vtype,
            'conf': self.conf,
            'asitem': self.asitem,
        }

        if not cleaned:  # add value and svalue if not cleaned
            kwargs['value'] = self.value
            kwargs['svalue'] = self.svalue

        result = Parameter(**kwargs)

        return result

    def clean(self):
        """Clean this param in removing values."""

        self._value = None
        self._svalue = None
