Description
-----------

Python class configuration tools in reflective and distributed concerns.

.. image:: https://img.shields.io/pypi/l/b3j0f.conf.svg
   :target: https://pypi.python.org/pypi/b3j0f.conf/
   :alt: License

.. image:: https://img.shields.io/pypi/status/b3j0f.conf.svg
   :target: https://pypi.python.org/pypi/b3j0f.conf/
   :alt: Development Status

.. image:: https://img.shields.io/pypi/v/b3j0f.conf.svg
   :target: https://pypi.python.org/pypi/b3j0f.conf/
   :alt: Latest release

.. image:: https://img.shields.io/pypi/pyversions/b3j0f.conf.svg
   :target: https://pypi.python.org/pypi/b3j0f.conf/
   :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/implementation/b3j0f.conf.svg
   :target: https://pypi.python.org/pypi/b3j0f.conf/
   :alt: Supported Python implementations

.. image:: https://img.shields.io/pypi/wheel/b3j0f.conf.svg
   :target: https://travis-ci.org/b3j0f/conf
   :alt: Download format

.. image:: https://travis-ci.org/b3j0f/conf.svg?branch=master
   :target: https://travis-ci.org/b3j0f/conf
   :alt: Build status

.. image:: https://coveralls.io/repos/b3j0f/conf/badge.png
   :target: https://coveralls.io/r/b3j0f/conf
   :alt: Code test coverage

.. image:: https://img.shields.io/pypi/dm/b3j0f.conf.svg
   :target: https://pypi.python.org/pypi/b3j0f.conf/
   :alt: Downloads

.. image:: https://readthedocs.org/projects/b3j0fconf/badge/?version=master
   :target: https://readthedocs.org/projects/b3j0fconf/?badge=master
   :alt: Documentation Status

Links
-----

- `Homepage`_
- `PyPI`_
- `Documentation`_

Installation
------------

pip install b3j0f.conf

Features
--------

This library provides a set of class configuration tools in order to ease development of systems based on configuration resources such as files, DB documents, etc. in a reflexive context.

Configuration process is in 2 steps:

- inject configuration resources (file, DB documents, etc.) in a Configurable class (with specific drivers which allows the Configurable class to be agnostic from configuration languages such as ini, json, xml, etc.),
- let the configurable class read properties from such configuration resources and apply values on a dedicated class which may be a associated to a business code. This last process can be automatically or manually thanks to the the apply_reconfiguration method.

Configuration
#############

The sub-module b3j0f.conf.params provides Configuration class in order to inject configuration resources in a Configurable class.

Configuration resources respect two levels of configuration such as the ini configuration model. Both levels are respectively:

- Category: permits to define a set of parameters unique by name.
- Parameter: couple of property name and value.

And all categories/options are embedded in a Configuration class.

Configuration and Categories are like dictionaries where key values are inner element names. Therefore, Parameter names are unique per Categories, and Category/Parameter names are unique per Configuration.

Parameter Overriding
####################

In a dynamic and complex way, one Configurable class can be bound to several Categories and Parameters. The choice is predetermined by the class itself. That means that one Configurable class can use several configuration resources and all/some/none Categories/Parameters in those resources. In such a way, the order is important because it permits to keep only last parameter values when parameters have the same name.

This overriding is respected by default with Configurable class inheritance. That means a sub class which adds a resource after its parent class resources indicates than all parameters in the final resources will override parameters in the parent class resources where names are the sames.

Configurable
############

A Configurable class is provided in the b3j0f.conf.configurable.core module. It permits to get parameters from a configuration resources.

Driver
######

Drivers are the mean to parse configuration resources, such as files, etc. By
default, conf drivers are able to parse json/ini files. Those last use a relative path given by the environment variable ``B3J0F_CONF_DIR`` or ``~/etc`` if not given.

Configurable Registry
#####################

A Configurable registry is provided in the b3j0f.conf.configurable.registry. It allows to use several Configurable classes once at a time.

Examples
--------

Bind the configuration file ``~/etc/myclass.conf`` to a business class ``MyClass`` (the relative path ``~/etc`` can be change thanks to the environment variable ``B3J0F_CONF_DIR``).

Configuration file
##################

The configuration file contains a category named ``MYCLASS`` containing the parameter ``myattr`` equals ``myvalue``.

.. code-block:: ini

    [MYCLASS]
    myattr=myvalue


With inheritance
################

.. code-block:: python

    from b3j0f.conf.configurable import Configurable
    from b3j0f.conf.configurable.decorator import conf_paths, add_category

    MYCATEGORY = 'MYCLASS'  # MyClass configuration category
    MYCONF = 'myclass.conf'  # MyClass configuration file

    # define the configurable business class
    @add_category(MYCATEGORY)  # set configuration file category
    @conf_paths(MYCONF)  # set conf path
    class MyClass(Configurable): pass

    # instantiate the business class
    myclass = MyClass()

    # check if myattr equals 'myvalue'
    assert myclass.myattr == 'myvalue'

Without inheritance
###################

.. code-block:: python

    from b3j0f.conf.configurable import Configurable

    MYCATEGORY = 'MYCLASS'  # MyClass configuration category
    MYCONF = 'myclass.conf'  # MyClass configuration file

    # instantiate a business class
    class MyClass(object): pass
    myclass = MyClass()

    # apply configuration to the business class
    Configurable(
        to_configure=myclass,
        conf_paths=MYCONF,
        unified_category=MYCATEGORY
    )

    # check if myattr equals 'myvalue'
    assert myclass.myattr == 'myvalue'

Perspectives
------------

- wait feedbacks during 6 months before passing it to a stable version.
- Cython implementation.

Donation
--------

.. image:: https://cdn.rawgit.com/gratipay/gratipay-badge/2.3.0/dist/gratipay.png
   :target: https://gratipay.com/b3j0f/
   :alt: I'm grateful for gifts, but don't have a specific funding goal.

.. _Homepage: https://github.com/b3j0f/conf
.. _Documentation: http://b3j0fconf.readthedocs.org/en/master/
.. _PyPI: https://pypi.python.org/pypi/b3j0f.conf/
