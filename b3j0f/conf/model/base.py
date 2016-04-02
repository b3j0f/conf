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

__all__ = ['ModelElement', 'CompositeModelElement']

from b3j0f.utils.version import OrderedDict


class ModelElement(object):
    """Base configuration elementParameter.

    Use a name and a provide a python value in ordr to ease serialization.

    A model element uses a local flag in order to indicates if it has been
    created with the upper composite model element or if it has been added after
    updating."""

    class Error(Exception):
        """Handle ModelElement errors."""

    __slots__ = ()

    def copy(self, *args, **kwargs):
        """Copy this model element and contained elements if they exist."""

        for slot in self.__slots__:
            attr = getattr(self, slot)
            if slot[0] == '_':  # convert protected attribute name to public
                slot = slot[1:]
            if slot not in kwargs:
                kwargs[slot] = attr

        result = type(self)(*args, **kwargs)

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
                if hasattr(self, __slot__):
                    __slot__ = __slot__[1:]

                else:
                    continue

            slotattr = getattr(self, __slot__)
            slotsrepr = '{0}{1}={2}, '.format(slotsrepr, __slot__, slotattr)

        if slotsrepr:
            slotsrepr = slotsrepr[:-2]

        result = '{0}[{1}]'.format(type(self).__name__, slotsrepr)

        return result

    def update(self, other, copy=True, *args, **kwargs):
        """Update this element related to other element.

        :param other: same type than this.
        :param bool copy: copy other before update attributes.
        :param tuple args: copy args.
        :param dict kwargs: copy kwargs.
        :return: this"""

        if other:  # dirty hack for python2.6

            if isinstance(other, self.__class__):

                if copy:
                    other = other.copy(*args, **kwargs)

                for slot in other.__slots__:
                    attr = getattr(other, slot)
                    if attr is not None:
                        setattr(self, slot, attr)

            else:
                raise TypeError(
                    'Wrong element to update with {0}: {1}'.format(self, other)
                )

        return self


class CompositeModelElement(ModelElement, OrderedDict):
    """Model element composed of model elements."""

    __contenttype__ = ModelElement  #: content type.

    __slots__ = ModelElement.__slots__

    def __init__(self, melts=None):
        """
        :param tuple melts: model elements to add.
        """

        super(CompositeModelElement, self).__init__({})

        if melts is not None:
            for melt in melts:
                self[melt.name] = melt

    def __deepcopy__(self, _):

        return self.copy()

    def __getattr__(self, key):
        """Try to delegate key attribute to content name."""
        result = None

        if key in self.__slots__:
            result = super(CompositeModelElement, self).__getattribute__(key)

        else:
            try:
                result = self[key]

            except KeyError:
                raise AttributeError(
                    '\'{0}\' object has no attribute \'{1}\''.format(
                        self.__class__, key
                    )
                )

        return result

    def __i(self, other, func):
        """Process input other with input func.

        :param ModelElement(s) other: other ModelElement(s) to process.
        :param func: function to apply on a ModelElement.
        :return: self.
        :raise: TypeError if other is not a ModelElement(s)."""

        if isinstance(other, type(self)):
            other = tuple(other)

        elif isinstance(other, self.__contenttype__):
            other = (other, )

        for melt in list(other):
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
            other=other, func=lambda melt: self.__setitem__(melt.name, melt)
        )

    def __isub__(self, other):
        """Remove a set of ModelElement in this content.

        :param ModelElement(s) other: ModelElement(s) to remove from this.
        :return: self.
        :raise: TypeError if other is not a ModelElement(s)."""

        return self.__i(other=other, func=lambda melt: self.pop(melt.name))

    def __ixor__(self, other):
        """Put other element(s) which are not registered in this.

        :param ModelElement(s) other: element(s) to put in this content.
        :return: self.
        :raise: TypeError if other is not a ModelElement(s)."""

        return self.__i(
            other=other,
            func=lambda melt:
            melt.name not in self and self.__setitem__(melt.name, melt)
        )

    def __repr__(self):

        result = super(CompositeModelElement, self).__repr__()

        result += OrderedDict.__repr__(self)[len(self.__class__.__name__) + 2: -2]

        return result

    def copy(self, *args, **kwargs):

        melts = [melt.copy() for melt in self.values()]

        result = super(CompositeModelElement, self).copy(
            melts=melts, *args, **kwargs
        )

        return result

    def update(self, other, copy=True, *args, **kwargs):
        """Update this composite model element with other element content.

        :param other: element to update with this. Must be the same type of this
            or this __contenttype__.
        :param bool copy: copy other before updating.
        :return: self"""

        super(CompositeModelElement, self).update(
            other, copy=copy, *args, **kwargs
        )

        if other:  # dirty hack for python2.6
            contents = []

            if isinstance(other, self.__class__):
                contents = list(other.values())

            elif isinstance(other, self.__contenttype__):
                contents = [other]

            else:
                raise TypeError(
                    'Wrong element to update with {0}: {1}'.format(self, other)
                )

            for content in contents:

                selfcontent = self.get(content.name)

                if selfcontent is None:

                    if copy:
                        content = content.copy(local=False)
                    self[content.name] = content

                else:
                    selfcontent.update(content, copy=copy, *args, **kwargs)

        return self

    @property
    def params(self):
        """Get set of parameters by names.

        :rtype: dict"""

        result = {}

        for content in list(self.values()):

            if isinstance(content, CompositeModelElement):
                cparams = content.params

                for cpname in cparams:
                    cparam = cparams[cpname]

                    if cpname in result:
                        result[cpname].update(cparam)

                    else:
                        result[cpname] = cparam.copy()

            elif content.name in result:
                result[content.name].update(content)

            else:
                result[content.name] = content.copy()

        return result
