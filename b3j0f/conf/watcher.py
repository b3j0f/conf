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

__all__ = [
    'add_configurable', 'remove_configurable',
    'on_update_conf_file',
    'Watcher',
    'get_watcher', 'start_watch', 'stop_watch', 'change_sleeping_time'
]


try:
    from threading import Timer
except ImportError:
    from dummythreading import Timer

from stat import ST_MTIME

from os import stat
from os.path import exists, expanduser

from b3j0f.conf.params import Configuration, Parameter, Category
from b3j0f.conf.configurable.core import Configurable

#: Dictionary of (mtime, configurables) by configuration file.
_CONFIGURABLES_BY_CONF_FILES = {}
_MTIME_BY_CONF_FILES = {}


def add_configurable(configurable):
    """Add input configurable to list of watchers.

    :param Configurable configurable: configurable to add.
    """

    for conf_file in configurable.conf_files:

        conf_file = expanduser(conf_file)

        configurables = _CONFIGURABLES_BY_CONF_FILES.setdefault(
            conf_file, set())

        configurables.add(configurable)


def remove_configurable(configurable):
    """Remove configurable to list of watchers.

    :param Configurable configurable: configurable to remove.
    """

    for conf_file in configurable.conf_files:

        conf_file = expanduser(conf_file)

        configurables = _CONFIGURABLES_BY_CONF_FILES.get(conf_file)

        if configurables:
            configurables.remove(configurable)

            if not configurables:
                del _CONFIGURABLES_BY_CONF_FILES[conf_file]


def on_update_conf_file(conf_file):
    """Apply configuration on all configurables which watch input
    conf_file.

    :param str conf_file: configuration file to reconfigure.
    """

    conf_file = expanduser(conf_file)

    configurables = _CONFIGURABLES_BY_CONF_FILES.get(conf_file)

    if configurables:

        for configurable in configurables:

            configurable.apply_configuration(conf_file=conf_file)

# default value for sleeping_time
DEFAULT_SLEEPING_TIME = 5


class Watcher(Configurable):
    """Watches all sleeping_time.
    """

    CONF_FILE = 'configuration/watcher.conf'

    CATEGORY = 'WATCHER'
    SLEEPING_TIME = 'sleeping_time'

    DEFAULT_CONFIGURATION = Configuration(
        Category(
            CATEGORY,
            Parameter(SLEEPING_TIME, value=DEFAULT_SLEEPING_TIME, parser=int)
        )
    )

    def __init__(self, sleeping_time=DEFAULT_SLEEPING_TIME, *args, **kwargs):

        super(Watcher, self).__init__(*args, **kwargs)

        self._sleeping_time = sleeping_time
        self._timer = None

    @property
    def sleeping_time(self):
        return self._sleeping_time

    @sleeping_time.setter
    def sleeping_time(self, value):
        """Change value of sleeping_time.
        """

        self._sleeping_time = value
        # restart the timer
        self.stop()
        self.start()

    def _get_conf_files(self, *args, **kwargs):

        result = super(Watcher, self)._get_conf_files(*args, **kwargs)

        result.append(Watcher.CONF_FILE)

        return result

    def _conf(self, *args, **kwargs):

        result = super(Watcher, self)._conf(*args, **kwargs)

        result.add_unified_category(
            name=Watcher.CATEGORY,
            new_content=(
                Parameter(Watcher.SLEEPING_TIME, parser=int)))

        return result

    def run(self):
        global _CONFIGURABLES_BY_CONF_FILES

        for conf_file in _CONFIGURABLES_BY_CONF_FILES:

            # check file exists
            if exists(conf_file):
                # get mtime
                mtime = stat(conf_file)[ST_MTIME]
                # compare with old mtime
                old_mtime = _MTIME_BY_CONF_FILES.setdefault(conf_file, mtime)
                if old_mtime != mtime:
                    on_update_conf_file(conf_file)

    def _run(self):
        self._timer = Timer(self.sleeping_time, self._run)
        self._timer.start()
        self.run()

    def start(self):
        self._timer = Timer(self.sleeping_time, self._run)
        self._timer.start()

    def stop(self):
        if self._timer is not None:
            self._timer.cancel()


def get_watcher():
    """Get global watcher.

    :return: global watcher.
    :rtype: Watcher
    """

    global _WATCHER  # try to load a global watcher

    try:
        result = _WATCHER
    except NameError:  # init a new watcher if _WATCHER is undefined
        result = _WATCHER = Watcher()

    return result


def start_watch():
    """Start default watcher.
    """

    watcher = get_watcher()
    watcher.start()


def stop_watch():
    """Stop default watcher.
    """

    watcher = get_watcher()
    watcher.stop()


def change_sleeping_time(sleeping_time):
    """Change of sleeping_time for default watcher.
    """

    watcher = get_watcher()
    watcher.sleeping_time = sleeping_time
