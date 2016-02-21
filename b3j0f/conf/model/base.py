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

from b3j0f.utils.version import OrderedDict


class ModelElement(object):
    """Base configuration elementParameter.

    Use a name and a provide a python value in ordr to ease serialization.
    """

    class Error(Exception):
        """Handle ModelElement errors."""

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

    def __eq__(self, other):

        result = isinstance(other, self.__class__)

        if result:

            result = True
            for slot in self.__slots__:

                selfattr = getattr(self, slot)
                otherattr = getattr(other, slot)

                result = selfattr == otherattr

                if not result:
                    break

        return result

    def __ne__(self, other):

        return not self.__eq__(other)

    def __repr__(self):

        slotsrepr = ''

        for __slot__ in self.__slots__:

            if __slot__.startswith('_'):
                continue

            slotattr = getattr(self, __slot__)
            slotsrepr = '{0}{1}, '.format(slotsrepr, slotattr)

        else:
            if slotsrepr:
                slotsrepr = slotsrepr[:-2]

        result = '{0}({1})'.format(type(self).__name__, slotsrepr)

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

    def __i(self, other, func):
        """Process input other with input func.

        :param ModelElement(s) other: other ModelElement(s) to process.
        :param func: function to apply on a ModelElement.
        :return: self.
        :raise: TypeError if other is not a ModelElement(s)."""

        if isinstance(other, type(self)):
            other = tuple(other.content)

        elif isinstance(other, self.__contenttype__):
            other = (other, )

        for melt in other:
            if not isinstance(melt, self.__contenttype__):
                raise TypeError('Wrong element {0}'.format(melt))

            else:
                func(melt)

        return self

    def __iadd__(self, other):
        """Put ModelElement(s) in this content.

        :param ModelElement(s) other: other element(s) to put to this.
        :return: self.
        :raise: TypeError if other is not a ModelElement(s)."""

        return self.__i(
            other=other,
            func=lambda melt: self._content.__setitem__(melt.name, melt)
        )

    def __isub__(self, other):
        """Remove a set of ModelElement in this content.

        :param ModelElement(s) other: ModelElement(s) to remove from this.
        :return: self.
        :raise: TypeError if other is not a ModelElement(s)."""

        return self.__i(
            other=other,
            func=lambda melt: self._content.pop(melt.name)
        )

    def __ixor__(self, other):
        """Put other element(s) which are not registered in this.

        :param ModelElement(s) other: element(s) to put in this content.
        :return: self.
        :raise: TypeError if other is not a ModelElement(s)."""

        return self.__i(
            other=other,
            func=lambda melt:
            melt.name not in self and self._content.__setitem__(
                melt.name, melt
            )
        )

    def __repr__(self):

        result = super(CompositeModelElement, self).__repr__()

        result = '{0}[{1}]'.format(result, self._content)

        return result

    def names(self):
        """Get content names."""

        return tuple(self._content.keys())

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

        self._content.clear()

        self += value

    def put(self, value):
        """Put a content value and return the previous one if exist.

        :param ModelElement value: model element to put in this.
        :return: previous model element registered at the same name.
        :rtype: ModelElement
        """

        result = self.get(value.name)

        self += value

        return result

    def clean(self, *args, **kwargs):

        for content in self._content.values():

            content.clean(*args, **kwargs)

    def copy(self, cleaned=False, *args, **kwargs):

        result = super(CompositeModelElement, self).copy(*args, **kwargs)

        for content in self._content.values():

            result += content.copy(cleaned=cleaned)

        return result

    def pop(self, name):
        """Remove an element by name and return it.

        :param str name: corresponding element name to remove.
        :return: corresponding element name.
        :rtype: ModelElement

        :raises: KeyError if name is not registered in this."""

        return self._content.pop(name)

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
