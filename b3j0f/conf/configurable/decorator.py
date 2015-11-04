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

__all__ = ['confpaths', 'add_category']

from b3j0f.annotation import PrivateInterceptor, Annotation

from .core import Configurable
from ..model import Category


def confpaths(*paths):
    """Configurable decorator which adds path paths to a Configurable.

    :param paths: conf resource pathes to add to a Configurable.
    :type paths: list of str

    Example:
    >>> confpaths('test0', 'test1')(Configurable)().paths[:-2]
    ['test0', 'test1']
    """

    def add_paths(cls):
        # add _get_paths method to configurable classes
        if issubclass(cls, Configurable):

            def _get_paths(self, *args, **kwargs):
                # get super result and append paths
                result = super(cls, self)._get_paths()
                result += paths

                return result

            cls._get_paths = _get_paths

        else:
            raise Configurable.Error(
                "class {0} is not a Configurable class".format(cls)
            )

        return cls

    return add_paths


class ClassConfiguration(Annotation):

    def __init__(self, conf, unified=True, useclsconf=True, *args, **kwargs):

        super(ClassConfiguration, self).__init__(*args, **kwargs)

    def _set_target(self):
        pass


def add_category(name, content=None, unified=True):
    """Add a category to a configurable configuration.

    :param str name: category name.
    :param content: category or list of parameters to add to the new category.
    :param bool unified: if True (by default), the new category is unified from
        previous conf.
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
                "class {0} is not a Configurable class".format(cls)
            )

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


class Configuration(PrivateInterceptor):
    """Annotation dedicated to bind a configurable to all class instances."""

    def __init__(
        self, paths=None, conf=None, store=False, configurable=None,
        configurablecls=Configurable, confparams=None, *args, **kwargs
    ):

        super(Configuration, self).__init__(*args, **kwargs)

        self.confparams = {} if confparams is None else confparams

        if configurable is None:
            self.configurable = self.configurablecls(
                store=store, paths=paths, conf=conf
            )
        else:
            self.configurable = configurable

    def _interception(self, joinpoint):

        result = joinpoint.proceed()

        self.configurable.to_configure.append(result)

        return result
