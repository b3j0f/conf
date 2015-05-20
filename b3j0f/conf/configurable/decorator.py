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

__all__ = ['conf_paths', 'add_category']


from b3j0f.conf.configurable.core import Configurable
from b3j0f.conf.params import Category, ParamList


def conf_paths(*conf_paths):
    """Configurable decorator which adds conf_path paths to a Configurable.

    :param paths: conf resource pathes to add to a Configurable.
    :type paths: list of str

    Example:
    >>> conf_paths('test0', 'test1')(Configurable)().conf_paths[:-2]
    ['test0', 'test1']
    """

    def add_conf_paths(cls):
        # add _get_conf_paths method to configurable classes
        if issubclass(cls, Configurable):

            def _get_conf_paths(self, *args, **kwargs):
                # get super result and append conf_paths
                result = super(cls, self)._get_conf_paths()
                result += conf_paths

                return result

            cls._get_conf_paths = _get_conf_paths

        else:
            raise Configurable.Error(
                "class {0} is not a Configurable class".format(cls))

        return cls

    return add_conf_paths


def add_category(name, unified=True, content=None):
    """Add a category to a configurable configuration.

    :param str name: category name.
    :param bool unified: if True (by default), the new category is unified from
        previous conf.
    :param content: category or list of parameters to add to the new category.
    :type content: Category or list(Parameter)
    """

    def add_conf(cls):

        if issubclass(cls, Configurable):

            def _conf(self, *args, **kwargs):

                result = super(cls, self)._conf(*args, **kwargs)

                if unified:
                    result.add_unified_category(name=name, new_content=content)
                else:
                    category = Category(name=name)
                    if content is not None:
                        category += content
                    result += category

                return result

            cls._conf = _conf

        else:
            raise Configurable.Error(
                "class {0} is not a Configurable class".format(cls))

        return cls

    return add_conf


def add_config(config, unified=True):
    """Add multiple categories to a configurable configuration.

    :param dict config: dict where keys are catogories names, and values
        categories content.
    :param bool unified: if True (by default), the new category is unified from
        previous conf.
    """

    def _add_unified(result, name, content):
        result.add_unified_category(name=name, new_content=content)
        return result

    def _add_not_unified(result, name, content):
        category = Category(name=name)

        if content is not None:
            category += content

        result += category

        return result

    def _add_category(result, name, content, unified):
        if isinstance(content, ParamList):
            result.add_param_list(name=name, content=content)

        else:
            if unified:
                result = _add_unified(result, name, content)

            else:
                result = _add_not_unified(result, name, content)

        return result

    def _conf(self, *args, **kwargs):
        result = super(type(self), self)._conf(*args, **kwargs)

        for name in config.keys():
            result = _add_category(result, name, config[name], unified)

        return result

    def add_conf(cls):
        if issubclass(cls, Configurable):
            cls._conf = _conf

        else:
            raise Configurable.Error(
                'class {0} is not a Configurable class'.format(cls)
            )

        return cls

    return add_conf
