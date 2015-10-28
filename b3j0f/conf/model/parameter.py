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


from b3j0f.utils.version import basestring
from b3j0f.utils.path import lookup

from json import loads as jsonloads

from re import compile as re_compile


class Parameter(object):
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

    CONF_SUFFIX = '::conf'  #: parameter configuration name.

    PARAM_NAME_REGEX = '[a-zA-Z_][a-zA-Z0-9_]*'  #: simple name validation.
    #: simple name regex compiler.
    _PARAM_NAME_COMPILER = re_compile(PARAM_NAME_REGEX)

    class Error(Exception):
        """Handle Parameter errors."""

    def __init__(
            self, name, vtype=object, parser=None, value=None, conf=None,
            critical=False, local=True, asitem=None
    ):
        """
        :param name: depends on type:
            - str: unique by category.
            - regex: designates a group of parameters with a matching name and
                common properties (parser, value, conf, etc.).
        :param type vtype: parameter value type.
        :param callable parser: param test deserializer which takes in param
            a str.
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

        # init public attributes
        self.name = name
        self.vtype = vtype
        self.conf = conf
        self.parser = parser
        self.critical = critical
        self.local = local
        self.asitem = asitem
        self.value = value

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

        if isinstance(value, basestring):

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
    def value(self):
        """Get parameter value.

        :return: parameter value.
        """
        return self._value

    @value.setter
    def value(self, value):
        """Change of parameter value.

        If an error occured, the error is available from the property error.

        :param value: new value to use. If value is a str and not parable by
            this parameter, the value becomes the parsing exception.
        :raises: Parameter.Error for any error occuring while changing of value
        .
        """

        self._error = None  # nonify error.

        finalvalue = None  # final value to compare with self type

        if isinstance(value, basestring) and self.parser is not None:
            # parse value if str and if parser exists

            try:
                finalvalue = self.parser(value)
            except Exception as ex:
                self._error = ex
                raise Parameter.Error(
                    'Impossible to parse value {0} with {1}.'.format(
                        value, self
                    )
                ).with_traceback(ex.__traceback__)

        else:
            finalvalue = value

        # check type
        if finalvalue is None or isinstance(finalvalue, self.vtype):

            # apply conf if necessary
            if finalvalue is not None and self.conf is not None:
                finalvalue = finalvalue(**self.conf)

            # update value property
            self._value = finalvalue

        else:  # raise wrong type error
            error = Parameter.Error(
                'Wrong value type of {0}. {1} expected.'.format(
                    finalvalue, self.vtype
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
            "name": name,
            "parser": self.parser
        }

        if not cleaned:
            kwargs["value"] = self.value

        result = Parameter(**kwargs)

        return result

    def clean(self):
        """Clean this param in removing values."""

        self._value = None

    @staticmethod
    def bool(value):
        """Boolean value parser.

        :param str value: value to parse.
        :return: True if value in [True, true, 1]. False Otherwise.
        :rtype: bool
        """

        return value == 'True' or value == 'true' or value == '1'

    @staticmethod
    def path(value):
        """Python class path value parser.

        :param str value: python class path to parse.
        :return: lookup(value).
        """

        return lookup(value)

    @staticmethod
    def json(value):
        """Get a data from a json data format.

        :param str value: json format to parse.
        :return: data.
        :rtype: str, list, dict, int, float or bool
        """

        return jsonloads(value)

    @staticmethod
    def _typedjson(value, cls):
        """Private static method which uses the json method and check if result
        inherits from the cls. Otherwise, raise an error.

        :param str value: value to parse in a json format.
        :param type cls: expected result class.
        :return: parsed value.
        :rtype: cls
        """

        result = Parameter.json(value)

        if not isinstance(result, cls):
            raise Parameter.Error(
                'Wrong type: {0}. {1} expected.'.format(value, cls)
            )

        return result

    @staticmethod
    def dict(value):
        """Get a dict from a dict json format.

        :param str value: dictionary json format to parse.
        :return: parsed dictionary.
        :rtype: dict
        :raises: Parameter.Error if value is not a dict json format.
        """

        return Parameter._typedjson(value, dict)

    @staticmethod
    def array(value):
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
            result = Parameter._typedjson(value, list)

        else:
            result = list(value.split(','))

        return result
