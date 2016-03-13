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

from unittest import main

from ..base import FileConfDriver, CONF_DIRS
from ...test.base import ConfDriverTest
from ....model.param import Parameter

from pickle import load, dump

from os import remove
from os.path import exists, join


class TestFileConfDriver(FileConfDriver):
    """Configuration file driver for test."""

    def resource(self):

        return {}

    def _cnames(self, resource):

        return resource.keys()

    def _params(self, resource, cname):

        result = [
            Parameter(pname, svalue=resource[cname][pname])
            for pname in resource[cname]
        ]

        return result

    def _pathresource(self, rscpath):

        result = None

        with open(rscpath, 'rb') as handle:

            result = load(handle)

        return result

    def _setconf(self, resource, rscpath, conf):

        for cat in conf.values():
            for param in cat.values():
                resource.setdefault(cat.name, {})[param.name] = param.svalue

        with open(rscpath, 'wb') as handle:

            dump(resource, handle)


class FileConfDriverTest(ConfDriverTest):
    """Configuration Manager unittest class."""

    __driverclass__ = TestFileConfDriver

    def setUp(self):

        super(FileConfDriverTest, self).setUp()

        last_conf_dir = CONF_DIRS[-1]

        for path in self.paths:

            rscpath = join(last_conf_dir, path)

            with open(rscpath, 'w+') as _:
                pass

    def tearDown(self):

        for path in self.paths:

            for rscpath in self.driver.rscpaths(path):

                if exists(rscpath):
                    remove(rscpath)


if __name__ == '__main__':
    main()
