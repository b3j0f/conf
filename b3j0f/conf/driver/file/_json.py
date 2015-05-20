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

__all__ = ['JSONConfDriver']


try:
    from json import loads, dump
except ImportError:
    from simplejson import loads, dump

from b3j0f.conf.driver.file.core import FileConfDriver


class JSONConfDriver(FileConfDriver):
    """Manage json configuration.
    """

    __register__ = True  #: Register it automatically among global managers.

    def _has_category(
        self, conf_resource, category, logger, *args, **kwargs
    ):
        return category.name in conf_resource

    def _has_parameter(
        self, conf_resource, category, param, logger,
        *args, **kwargs
    ):
        return param.name in conf_resource[category.name]

    def _get_conf_resource(
        self, logger, conf_path=None, *args, **kwargs
    ):
        result = {}

        if conf_path is not None:
            result = None

            path = FileConfDriver.get_path(conf_path)

            try:
                with open(path, 'r') as handle:
                    content = handle.read()
                    result = loads(content)

            except Exception:
                pass

        return result

    def _get_categories(self, conf_resource, logger, *args, **kwargs):
        return conf_resource.keys()

    def _get_parameters(
        self, conf_resource, category, logger, *args, **kwargs
    ):
        return conf_resource[category.name].keys()

    def _get_value(
        self, conf_resource, category, param, *args, **kwargs
    ):
        return conf_resource[category.name][param.name]

    def _set_category(
        self, conf_resource, category, logger, *args, **kwargs
    ):
        conf_resource.setdefault(category.name, {})

    def _set_parameter(
        self, conf_resource, category, param, logger,
        *args, **kwargs
    ):
        conf_resource[category.name][param.name] = param.value

    def _update_conf_resource(
        self, conf_resource, conf_path, *args, **kwargs
    ):

        path = FileConfDriver.get_path(conf_path)

        try:
            with open(path, 'w') as handle:
                dump(conf_resource, handle)

        except Exception:
            pass
