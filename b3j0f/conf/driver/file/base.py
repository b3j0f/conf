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

__all__ = ['FileConfDriver']

"""This module specifies file drivers.

They work relatively to system/user conf directories and an optional conf
directory given by the environment variable ``B3J0F_CONF_DIR``.
"""

from os import environ, getenv
from os.path import exists, join, expanduser, sep, abspath

from ..base import ConfDriver

from sys import prefix


CONF_DIRS = []  #: all config directories


def _addconfig(config, *paths):
    """Add path to CONF_DIRS if exists."""

    for path in paths:
        if path is not None and exists(path):
            config.append(path)

# add installation directory
_addconfig(CONF_DIRS, join(sep, *(__file__.split(sep)[:-3] + ['data'])))

# add unix system conf
_addconfig(CONF_DIRS, join(sep, 'etc'), join(sep, 'usr', 'local', 'etc'))

_addconfig(
    CONF_DIRS,
    join(prefix, '.config'), join(prefix, 'config'), join(prefix, 'etc')
)

# add XDG conf dirs
_addconfig(CONF_DIRS, getenv('XDG_CONFIG_HOME'), getenv('XDG_CONFIG_DIRS'))

# add windows conf dirs
_addconfig(
    CONF_DIRS,
    getenv('APPDATA'), getenv('PROGRAMDATA'), getenv('LOCALAPPDATA')
)

HOME = environ.get(
    'HOME',  # unix-like
    environ.get(
        'USERPROFILE',  # windows-like
        expanduser('~')
    )  # default
)  #: set user home directory

# add usr config
_addconfig(
    CONF_DIRS, join(HOME, '.config'), join(HOME, 'config'), join(HOME, 'etc')
)

_addconfig(CONF_DIRS, '.')  # add current directory

B3J0F_CONF_DIR = 'B3J0F_CONF_DIR'  #: conf dir environment variable name.

if B3J0F_CONF_DIR in environ:  # add b3j0F_CONF_DIR if necessary
    CONF_DIRS.append(environ[B3J0F_CONF_DIR])  #: conf dir environment variable


class FileConfDriver(ConfDriver):
    """Conf Manager dedicated to files."""

    def rscpaths(self, path):

        result = list(
            join(conf_dir, path) for conf_dir in CONF_DIRS
            if exists(join(conf_dir, path))
        )

        rel_path = expanduser(path)  # add relative path
        if exists(rel_path):
            result.append(rel_path)

        else:
            abs_path = abspath(path)  # add absolute path
            if exists(abs_path):
                result.append(abs_path)

        return result
