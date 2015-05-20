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

from tempfile import NamedTemporaryFile

from os import remove

from b3j0f.utils.ut import UTCase

from b3j0f.conf.configurable.core import Configurable
from b3j0f.conf.configurable.registry import ConfigurableRegistry
from b3j0f.conf.driver.file.core import FileConfDriver


class TestConfigurable(Configurable):
    pass


class TestRegistry(ConfigurableRegistry):

    def _get_conf_paths(self, *args, **kwargs):

        result = super(TestRegistry, self)._get_conf_paths(*args, **kwargs)
        result.append(NamedTemporaryFile().name)
        return result


class ManagerTest(UTCase):

    def setUp(self):
        pass

    def test_apply_configuration(self):

        driver = TestRegistry()

        conf_path = FileConfDriver.get_path(driver.conf_paths[-1])

        configurable_name = 'test'
        full_configurable_name = '{0}{1}'.format(
            configurable_name, ConfigurableRegistry.CONFIGURABLE_SUFFIX)
        configurable_type_name = '{0}{1}'.format(
            configurable_name, ConfigurableRegistry.CONFIGURABLE_TYPE_SUFFIX)
        # ensure configurable doesn't exis
        self.assertFalse(configurable_name in driver)

        self.assertEqual(len(driver.configurables), 0)
        self.assertEqual(len(driver.configurable_types), 0)

        driver[configurable_name] = Configurable()

        self.assertTrue(driver[configurable_name].auto_conf)

        configurable_path = "b3j0f.conf.configurable.core.Configurable"

        with open(conf_path, 'w+') as conf_file:
            conf_file.write("[MANAGER]")
            # set configurable
            conf_file.write("\n{0}=".format(full_configurable_name))
            conf_file.write(configurable_path)
            # set configurable type
            conf_file.write("\n{0}=".format(configurable_type_name))
            conf_file.write(configurable_path)
            # set sub-configurable auto_conf to false
            configurable_category = \
                ConfigurableRegistry.get_configurable_category(
                    configurable_name)
            conf_file.write("\n[{0}]".format(configurable_category))
            conf_file.write("\nauto_conf=false")

        driver.apply_configuration()

        remove(conf_path)

        self.assertEqual(len(driver.configurables), 1)
        self.assertEqual(len(driver.configurable_types), 1)

        # check if configurable and short attribute exist
        self.assertFalse(driver[configurable_name].auto_conf)
        self.assertTrue(isinstance(driver[configurable_name], Configurable))

        # check if configurable type exist
        self.assertEqual(
            driver.configurable_types[configurable_name], Configurable)

        # change type with str or Configurable class
        driver.configurable_types[configurable_name] = configurable_path
        self.assertEqual(
            driver.configurable_types[configurable_name], Configurable)
        driver.configurable_types[configurable_name] = Configurable
        self.assertEqual(
            driver.configurable_types[configurable_name], Configurable)

        # change type in order to do not remove old value
        driver.test_configurable_type = Configurable
        self.assertTrue(isinstance(driver[configurable_name], Configurable))
        driver.test = configurable_path
        self.assertTrue(isinstance(driver[configurable_name], Configurable))
        driver.test = Configurable
        self.assertTrue(isinstance(driver[configurable_name], Configurable))
        driver.test = Configurable()
        self.assertTrue(isinstance(driver[configurable_name], Configurable))

        self.assertEqual(len(driver.configurables), 1)
        self.assertEqual(len(driver.configurable_types), 1)

        # change type value in order to remove old value
        driver.configurable_types[configurable_name] = TestConfigurable
        self.assertFalse(configurable_name in driver)
        self.assertEqual(
            driver.configurable_types[configurable_name], TestConfigurable)

        self.assertEqual(len(driver.configurables), 0)
        self.assertEqual(len(driver.configurable_types), 1)

        driver[configurable_name] = Configurable()
        self.assertFalse(configurable_name in driver)

        self.assertEqual(len(driver.configurables), 0)
        self.assertEqual(len(driver.configurable_types), 1)

if __name__ == '__main__':
    main()
