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

__all__ = ['MetaConfigurable', 'Configurable', 'ConfigurableError']


from logging import Formatter, getLogger, FileHandler, Filter

from os.path import join, sep

from b3j0f.utils.property import addproperties

from ..model.configuration import Configuration
from ..model.category import Category
from ..model.parameter import Parameter

from .core import Configurable


def _updatelogger(self, kwargsvalue, name):
    """Renew self logger."""
    self._logger = self.newlogger()


@addproperties(
    names=[
        'log_debug_format', 'log_info_format', 'log_warning_format',
        'log_error_format', 'log_critical_format', 'log_name', 'log_path'
    ], afset=_updatelogger
)
@addproperties(names=['logger'])
class Logger(Configurable):
    """Manage class conf synchronisation with conf resources."""

    LOG = 'LOG'  #: log attribute name.

    LOG_NAME = 'log_name'  #: logger name property name.
    LOG_LVL = 'log_lvl'  #: logging level property name.
    LOG_PATH = 'log_path'  #: logging path property name.
    LOG_DEBUG_FORMAT = 'log_debug_format'  #: debug log format property name.
    LOG_INFO_FORMAT = 'log_info_format'  #: info log format property name.
    LOG_WARNING_FORMAT = 'log_warning_format'  #: warn log format property name
    LOG_ERROR_FORMAT = 'log_error_format'  #: error log format property name.
    LOG_CRITICAL_FORMAT = 'log_critical_format'  #: crit log format property.

    # log messages format.
    #: debug message format.
    DEBUG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] \
[%(process)d] [%(thread)d] [%(pathname)s] [%(lineno)d] %(message)s"
    #: info message format.
    INFO_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    WARNING_FORMAT = INFO_FORMAT  #: warning message format.
    ERROR_FORMAT = WARNING_FORMAT  #: error message format.
    CRITICAL_FORMAT = ERROR_FORMAT  #: critical message format.

    def __init__(
            self,
            log_lvl='INFO', log_name=None, log_path='.',
            log_info_format=INFO_FORMAT,
            log_debug_format=DEBUG_FORMAT, log_warning_format=WARNING_FORMAT,
            log_error_format=ERROR_FORMAT, log_critical_format=CRITICAL_FORMAT,
            *args, **kwargs
    ):
        """
        :param str log_lvl: logging level. Default is INFO.
        :param str log_name: logger name. Default is configurable class lower
            name.
        :param str log_path: logging file path. Default is current directory.
        :param str log_info_format: info logging level format.
        :param str log_debug_format: debug logging level format.
        :param str log_warning_format: warning logging level format.
        :param str log_error_format: error logging level format.
        :param str log_critical_format: critical logging level format.
        """

        super(Logger, self).__init__(*args, **kwargs)

        # init protected attributes
        self._log_lvl = log_lvl
        self._log_path = log_path
        self._log_name = log_name if log_name else type(self).__name__.lower()
        self._log_debug_format = log_debug_format
        self._log_info_format = log_info_format
        self._log_warning_format = log_warning_format
        self._log_error_format = log_error_format
        self._log_critical_format = log_critical_format

        self._logger = self.newlogger()

    def newlogger(self):
        """Get a new logger related to self properties."""

        result = getLogger(self.log_name)
        result.setLevel(self.log_lvl)

        def sethandler(logger, lvl, path, _format):
            """Set right handler related to input lvl, path and format.

            :param Logger logger: logger on which add an handler.
            :param str lvl: logging level.
            :param str path: file path.
            :param str _format: logging message format.
            """

            class _Filter(Filter):
                """Ensure message will be given for specific lvl
                """
                def filter(self, record):
                    return record.levelname == lvl

            # get the rights formatter and filter to set on a file handler
            handler = FileHandler(path)
            handler.addFilter(_Filter())
            handler.setLevel(lvl)
            formatter = Formatter(_format)
            handler.setFormatter(formatter)

            # if an old handler exist, remove it from logger
            if hasattr(logger, lvl):
                old_handler = getattr(logger, lvl)
                logger.removeHandler(old_handler)

            logger.addHandler(handler)
            setattr(logger, lvl, handler)

        filename = self.log_name.replace('.', sep)
        path = join(self.log_path, '{0}.log'.format(filename))

        sethandler(result, 'DEBUG', path, self.log_debug_format)
        sethandler(result, 'INFO', path, self.log_info_format)
        sethandler(result, 'WARNING', path, self.log_warning_format)
        sethandler(result, 'ERROR', path, self.log_error_format)
        sethandler(result, 'CRITICAL', path, self.log_critical_format)

        return result

    def _clsconf(self, *args, **kwargs):

        result = super(Logger, self)._clsconf(*args, **kwargs)

        result += Category(
            Configurable.LOG,
            Parameter(name=Configurable.LOG_NAME, critical=True),
            Parameter(name=Configurable.LOG_PATH, critical=True),
            Parameter(name=Configurable.LOG_LVL, critical=True),
            Parameter(name=Configurable.LOG_DEBUG_FORMAT, critical=True),
            Parameter(name=Configurable.LOG_INFO_FORMAT, critical=True),
            Parameter(name=Configurable.LOG_WARNING_FORMAT, critical=True),
            Parameter(name=Configurable.LOG_ERROR_FORMAT, critical=True),
            Parameter(name=Configurable.LOG_CRITICAL_FORMAT, critical=True)
        )

        return result

    @property
    def log_lvl(self):
        """Get this logger lvl.

        :return: self logger lvl.
        :rtype: str
        """

        return self._log_lvl

    @log_lvl.setter
    def log_lvl(self, value):
        """Change of logging level.

        :param str value: new log_lvl to set up.
        """

        self._log_lvl = value

        self._logger.setLevel(self._log_lvl)

    @property
    def log_name(self):
        """Get this logger name.

        :return: self logger name.
        :rtype: str
        """

        return self._log_name

    @log_name.setter
    def log_name(self, value):
        """Change of logging name.

        :param str value: new log_name to set up.
        """

        self._log_name = value

        self._logger.setLevel(self._log_name)
