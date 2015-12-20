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

.. image:: https://landscape.io/github/b3j0f/conf/master/landscape.svg?style=flat
   :target: https://landscape.io/github/b3j0f/conf/master
   :alt: Code Health

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
- let the configurable class read properties from such configuration resources and apply values on a dedicated class which may be a associated to a business code. This last process can be done automatically or manually thanks to the the applyconfiguration method.

Configuration
#############

The sub-module b3j0f.conf.model provides Configuration class in order to inject configuration resources in a configurable class.

Configuration resources respect two levels of configuration same as the ini configuration model. Both levels are respectively:

- Category: permits to define a set of parameters unique by name.
- Parameter: couple of property name and value.

And all categories/parameters are embedded in a Configuration class.

Configuration and Categories are like dictionaries where key values are inner element names. Therefore, Parameter names are unique per Categories, and Category/Parameter names are unique per Configuration.

Parameter Overriding
####################

In a dynamic and complex way, one Configurable class can be bound to several Categories and Parameters. The choice is predetermined by the class itself. That means that one Configurable class can use several configuration resources and all/some/none Categories/Parameters in those resources. In such a way, the order is important because it permits to keep only last parameter values when parameters have the same name.

This overriding is respected by default with Configurable class inheritance. That means a sub class which adds a resource after its parent class resources indicates than all parameters in the final resources will override parameters in the parent class resources where names are the sames.

Name such as a regular expression
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Even if a parameter uses a name, it is possible to use this name such as a regular expression name.

In this case, while reading a configuration from a resource, all configuration parameters which match the regular expression will use the same attributes as defined in the parameter with the regular expression. And a name which is the name from the configuration resource.

Parser
~~~~~~

The module b3j0f.conf.model.parser provides parsers used to deserialize parameter values.

Default parser is the expression parser.

Expression parser
~~~~~~~~~~~~~~~~~

The parser ``exprparser`` permits to write simple expressions using the python builtin functions except those able to do I/O operations like the ``open`` function.

Such expression is prefixed by the character `=`.

In such expression, you can call back other configuration parameter in using this format (thanks to the idea from the pypi config_ project) related to a Configuration model:

- ``#{path}`` where ``path`` corresponds to a python object path. For example, `#sys.maxsize` designates the max size of the integer on the host machine (attribute ``maxsize`` of the module ``sys``).
- ``@[[://{path}/]{cat}].{param}`` where ``cat`` designates a configuration category name, and ``param`` designates related parameter value.
- ``@{param}`` where ``param`` designates a final parameter value (last overidden value).

Configurable
############

A Configurable class is provided in the b3j0f.conf.configurable.core module. It permits to get parameters from a configuration resources.

It uses a Configuration model and drivers.

Driver
######

Drivers are the mean to parse configuration resources, such as files, etc. from a configuration model provided by a Configurable object.
By default, conf drivers are able to parse json/ini files. Those last use a relative path given by the environment variable ``B3J0F_CONF_DIR`` or from directories (in this order) ``/etc``, ``/usr/local/etc``, ``~/etc``, ``~/.config``, ``~/config`` or current execution directory.

Example
-------

Bind configuration files to an object
#####################################

Bind the configuration file ``~/etc/myclass.conf`` and ``~/.config/myclass.conf`` to a business class ``MyClass`` (the relative path ``~/etc`` can be change thanks to the environment variable ``B3J0F_CONF_DIR``).

The configuration file contains a category named ``MYCLASS`` containing the parameters:

- ``myattr`` equals ``'myvalue'``.
- ``six`` equals ``6``.
- ``twelve`` equals ``six * 2.0``.

Let the following configuration file ``~/etc/myclass.conf`` in ini format:

.. code-block:: ini

  [MYCLASS]
  myattr = myvalue
  twelve = = @six * 2.0

Let the following configuration file ``~/.config/myclass.conf`` in json format:

.. code-block:: json

  {
    "MYCLASS": {
      "six": 6
    }
  }

The following code permits to load upper configuration to a python object.

.. code-block:: python

    from b3j0f.conf import Configurable, Category

    # instantiate a business class
    @Configurable(paths='myclass.conf', conf=Category('MYCLASS'))
    class MyClass(object):
        pass

    myclass = MyClass()

    # assert attributes
    assert myclass.myattr == 'myvalue'
    assert myclass.six == 6
    assert myclass.twelve == 12

Configure several objects with one configurable
###############################################

.. code-block:: python

    from b3j0f.conf import getconfigurables

    class Test(object):
        pass

    toconfigure = list(Test() for _ in range(5))

    configurable = getconfigurables(myclass)[0]
    configurable.applyconfiguration(toconfigure=toconfigure)

    for item in toconfigure:
        assert item.six == 6

Reconfigure a configurable object
#################################

.. code-block:: python

    from b3j0f.conf import applyconfiguration

    myclass.six = 7

    applyconfiguration(myclass)

    assert myclass.six == 6

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
.. _config: https://pypi.python.org/pypi/config/
