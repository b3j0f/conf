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


from unittest import main

from b3j0f.utils.ut import UTCase

from ..log import Logger
from ...driver.test.base import TestConfDriver


class LoggerTest(UTCase):

    def setUp(self):

        self.logger = Logger()

    def test_loglvl(self):

        log_lvl = self.logger.logger.level

        self.assertEqual(log_lvl, self.logger.log_lvl)

        self.logger.log_lvl += 10

        self.assertEqual(log_lvl + 10, self.logger.log_lvl)

        self.assertEqual(self.logger.log_lvl, self.logger.logger.level)

    def test_override(self):
        """Test if overriden methods have change the logger parameter."""

        testself = self

        class MyTestConfDriver(TestConfDriver):
            """ConfDriver test function."""

            def getconf(self, logger, *args, **kwargs):

                testself.assertIs(logger, testself.logger.logger)

                return super(MyTestConfDriver, self).getconf(
                    logger=logger, *args, **kwargs
                )

        self.logger.getconf(drivers=[MyTestConfDriver()])


if __name__ == '__main__':
    main()
