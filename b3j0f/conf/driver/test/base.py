#!/usr/bin/env python
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

"""conf file driver UTs."""

from b3j0f.utils.ut import UTCase

from unittest import main

from ...model.conf import Configuration
from ...model.cat import Category
from ...model.param import Parameter

from ..base import ConfDriver


class TestConfDriver(ConfDriver):
    """Configuration driver for test."""

    def __init__(self):

        super(TestConfDriver, self).__init__()

        self.confbypath = {}

    def resource(self):

        return {}

    def _pathresource(self, rscpath):

        return self.confbypath[rscpath]

    def _cnames(self, resource):

        return list(resource)

    def _params(self, resource, cname):

        return resource[cname].values()

    def _setconf(self, conf, resource, rscpath):

        self.confbypath[rscpath] = conf

    def rscpaths(self, path):

        return [path]


class ConfDriverTest(UTCase):
    """Test the conf driver class."""

    __driverclass__ = TestConfDriver

    def setUp(self):

        self.count = 5
        self.driver = self.__driverclass__()
        self.paths = ['test{0}'.format(count) for count in range(self.count)]
        self.conf = Configuration(
            Category(
                'A',
                melts=[
                    Parameter('a', value=0, ptype=int),  # a is 0
                    Parameter('b', value=True, ptype=bool)
                ]
            ),  # b is overriden
            Category(
                'B',
                melts=[
                    Parameter('b', value=1, ptype=int),  # b is 1
                ]
            )
        )

    def test_rscpaths(self):
        """Test the method rscpaths."""

        for path in self.paths:

            rscpaths = self.driver.rscpaths(path=path)

            for rscpath in rscpaths:
                self.assertTrue(rscpath.endswith(path))

    def test_scenario(self):
        """Test a scenario of getting/putting configuration."""

        for path in self.paths:

            conf = self.driver.getconf(path=path)

            self.assertIsNone(conf)

            conf = self.driver.getconf(path=path, conf=self.conf)

            self.assertEqual(conf, self.conf)

            rscpaths = self.driver.rscpaths(path=path)

            for rscpath in rscpaths:

                self.assertTrue(rscpath.endswith(path))

                conf = self.conf.copy()
                conf += Category('test', melts=[Parameter('test')])

                self.driver.setconf(rscpath=rscpath, conf=conf)

            conf = self.driver.getconf(path=path)

            self.assertNotEqual(conf, self.conf)

            self.assertIn('test', conf)
            self.assertIn('test', conf['test'])


if __name__ == '__main__':
    main()
