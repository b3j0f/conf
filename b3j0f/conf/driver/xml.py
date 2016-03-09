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

"""XML configuration driver."""

from __future__ import absolute_import

__all__ = ['XMLConfDriver']

from xml.etree.ElementTree import fromstring, Element, ElementTree

from .base import ConfDriver


class XMLConfDriver(ConfDriver):
    """Manage xml resource configuration."""

    CONFIGURATION = 'configuration'
    PARAMETER = 'parameter'
    CATEGORY = 'category'

    def rscpaths(self, path):

        return [path]

    def resource(self):

        return ElementTree(Element(XMLConfDriver.CONFIGURATION))

    def _pathresource(self, rscpath):

        result = fromstring(rscpath)

        return result

    def _cnames(self, resource):

        result = list(
            cat.get('name') for cat in resource.iter(XMLConfDriver.CATEGORY)
        )

        return result

    def _params(self, resource, cname):

        query = '{0}[@name=\'{1}\']/{2}'.format(
            XMLConfDriver.CATEGORY,
            cname,
            XMLConfDriver.PARAMETER
        )

        result = list(
            (param.get('name'), param.get('svalue'))
            for param in resource.findall(query)
        )

        return result

    def _setconf(self, conf, resource, rscpath):

        for cat in conf.values():

            cquery = '{0}[@name=\'{1}\']'.format(
                XMLConfDriver.CATEGORY, cat.name
            )

            ecat = resource.find(cquery)

            if ecat is None:
                ecat = Element(XMLConfDriver.CATEGORY, name=cat.name)
                resource.getroot().append(ecat)

            for param in cat.values():

                pquery = '{0}[@name=\'{1}\']'.format(
                    XMLConfDriver.PARAMETER, param.name
                )

                eparam = ecat.find(pquery)

                if eparam is None:
                    eparam = Element(XMLConfDriver.PARAMETER, name=param.name)
                    ecat.append(eparam)

                if param.svalue is not None:
                    eparam.set('svalue', param.svalue)

        return resource.getroot().text
