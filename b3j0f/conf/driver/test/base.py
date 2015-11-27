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

    def __init__(self, count=5):

        self.count = count

        self.confbypath = {}

        for i in range(self.count):
            self.confbypath['{0}'.format(i)] = Configuration(
                Category(
                    'cat{0}'.format(i),
                    Parameter(name='param', value=i))
            )

    def _resource(self, rscpath, **_):
        """Get configuration resource from resource path.

        :param str rscpath: resource path.
        :param Logger logger: logger to use.
        """

        return self.confbypath[rscpath]

    def _cnames(self, resource, **_):
        """Get resource category names.

        :param resource: resource from where get category names.
        :param Logger logger: logger to use.
        :return: resource category names.
        :rtype: list
        """

        return resource.keys()

    def _params(self, resource, cname, **_):
        """Get list of (parameter name, parameter value) from a category name
        and a specific configuration resource.

        :param resource: resource from where get parameter names and values.
        :param str cname: related category name.
        :param Logger logger: logger to use.
        :return: list of resource parameter
        :rtype: list
        """

        result = []

        for pname in resource[cname]:
            parameter = resource[cname][pname]
            pvalue = parameter.value
            result.append((pname, pvalue))

        return result

    def rscpaths(self, path, **_):
        """Get resource paths related to input configuration path.

        :param str path: configuration path.
        :rtype: list
        """

        return [path]

    def _set_conf(self, conf, resource, rscpath, **_):
        """Set input conf to input resource.

        :param Configuration conf: conf to write to path.
        :param resource: driver configuration resource.
        :param str rscpath: specific resource path to use.
        :param Logger logger: used to log info/errors
        """

        self.confbypath[rscpath] = conf


class ConfDriverTest(UTCase):
    """Test the conf driver class."""

    def setUp(self):

        self.driver = TestConfDriver()

    def test_rscpaths(self):
        """Test the method rscpaths."""

        for path in self.driver.confbypath:

            rscpaths = self.driver.rscpaths(path=path)

            self.assertEqual(rscpaths, [path])

    def test__get_conf(self):
        """Test the method _get_conf."""

        for rscpath in self.driver.confbypath:

            conf = self.driver._get_conf(rscpath=rscpath)

            self.assertEqual(self.driver.confbypath[rscpath], conf)

    def test_get_conf(self):
        """Test the method get_conf."""

        for rscpath in self.driver.confbypath:

            conf = self.driver.get_conf(path=rscpath)

            print(conf, self.driver.confbypath[rscpath])
            self.assertEqual(self.driver.confbypath[rscpath], conf)

    def test_get_conf_old(self):
        """Test the method get_conf with an old conf."""

        for rscpath in self.driver.confbypath:

            driverconf = self.driver.confbypath[rscpath]

            conf = Configuration(Category('test'))

            self.assertEqual(len(conf), 1)

            self.driver.get_conf(path=rscpath, conf=conf)

            self.assertEqual(len(conf), len(driverconf) + 1)

    def test_empty_get_conf(self):
        """Test the method get_conf with a not existing confpath."""

        conf = self.driver.get_conf(path='notexist')

        self.assertIsNone(conf)


if __name__ == '__main__':
    main()
