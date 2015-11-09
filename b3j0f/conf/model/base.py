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

from __future__ import absolute_import

__all__ = ['ModelElement', 'CompositeModelElement']

from collections import Iterable, OrderedDict


class ModelElement(object):
    """Base configuration elementParameter.

    Use a name and a provide a python value in ordr to ease serialization.
    """

    __slots__ = ()

    def clean(self):
        """Clean this model element."""

        raise NotImplementedError()

    def copy(self, cleaned=False, *args, **kwargs):
        """Copy this model element and contained elements if they exist.

        :param bool cleaned: if True (default False) copy this element without
            parameter values/svalues.
        """

        result = type(self)(*args, **kwargs)

        if cleaned:
            result.clean()

        return result


class CompositeModelElement(ModelElement):
    """Model element composed of model elements."""

    __contenttype__ = ModelElement  #: content type.

    __slots__ = ('_content', ) + ModelElement.__slots__

    def __init__(self, *content):

        super(CompositeModelElement, self).__init__()

        # init protected attributes
        self._content = OrderedDict()

        self.content = content

    def __iter__(self):

        return iter(self._content.values())

    def __getitem__(self, key):

        if isinstance(key, ModelElement):
            key = key.name

        return self._content[key]

    def __setitem__(self, key, value):

        if isinstance(key, ModelElement):
            key = key.name

        self._content[key] = value

    def __delitem__(self, key):

        if isinstance(key, ModelElement):
            key = key.name

        del self._content[key]

    def __getattr__(self, key):

        result = None

        if key in self.__slots__:
            result = super(CompositeModelElement, self).__getattribute__(key)

        else:
            result = self._content[key]

        return result

    def __contains__(self, key):

        if isinstance(key, ModelElement):
            key = key.name

        return key in self._content

    def __len__(self):

        return len(self._content)

    def __iadd__(self, other):
        """Add content or conf content in self."""

        if isinstance(other, type(self)):
            self._content.update(other.content)

        elif isinstance(other, self.__contenttype__):
            self._content[other.name] = other

        else:
            if isinstance(other, Iterable):
                for modelelt in other:
                    self += modelelt

        return self

    def __isub__(self, other):

        if isinstance(other, ModelElement):
            other = (ModelElement)

        for modelelt in other:

            name = modelelt.name

            if name in self._content:
                del self._content[name]

        return self

    def __ixor__(self, other):

        if isinstance(other, ModelElement):
            other = (ModelElement)

        for modelelt in other:

            name = modelelt.name

            if name not in self._content:
                self._content[name] = modelelt

        return self

    def __repr__(self):

        result = '{0}({1})'.format(type(self).__name__, self._content)

        return result

    @property
    def content(self):
        """Get Content.

        :rtype: tuple
        """

        return tuple(self._content.values())

    @content.setter
    def content(self, value):
        """Change of content.

        :param ModelElement(s) value: new content to use.
        """

        if value is None:
            self._content.clear()

        else:

            if isinstance(value, ModelElement):
                value = (value, )

            for modelelt in value:
                self._content[modelelt.name] = modelelt

    def put(self, value):
        """Put a content value and return the previous one if exist.

        :param ModelElement value: model element to put in this.
        :return: previous model element registered at the same name.
        :rtype: ModelElement
        """

        result = self.get(value.name)

        self[value.name] = value

        return result

    def clean(self, *args, **kwargs):

        for content in self._content.values():

            content.clean(*args, **kwargs)

    def copy(self, cleaned=False, *args, **kwargs):

        result = super(CompositeModelElement, self).copy(*args, **kwargs)

        for content in self._content.values():

            result += content.copy(cleaned)

        return result

    def get(self, key, default=None):
        """Get a content value by its name.

        :param str key: content name.
        :param ModelElement default: default value if key is not registered.
        :return: related content model element.
        :rtype: ModelElement
        """

        return self._content.get(key, default)

    def setdefault(self, key, value):
        """Register a content value with specific name if key not already used.

        :param str key: content name.
        :param ModelElement value: model element to register.
        :return: existing model element or input value if no modelelt has
            been registered with key.
        :rtype: ModelElement
        """

        return self._content.setdefault(key, value)

    def clear(self):
        """Clear this composite model element from this content."""

        self._content.clear()
