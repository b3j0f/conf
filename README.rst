Description
-----------

Python object configuration library in reflective and distributed concerns.

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

This library provides a set of object configuration tools in order to ease development of systems based on configuration resources such as files, DB documents, etc. in a reflexive, functional and distributed context.

Configuration processing is done is in 5 steps with only two mandatories:

1. optional : configuration model specification. You define which parameters you want to setup (default value, type, etc.).
2. optional : configuration driver selection. You define the nature of configuration resources (xml, json, ini, etc.).
3. mandatory : configuration resource edition. You define your configuration resources (files, DB documents, etc.).
4. optional : bind a configurable to python object(s). You bind a configurable to objects to setup for a reflexive use.
5. mandatory : apply configuration to a python object. You setup your python objects.

In order to improve reflexive concerns, this library has been developed with very strong flexible features available at runtime.

It is possible to custom every parts directly at runtime with high speed execution concerns.

You can customize:

- parsing functions.
- drivers.
- configuration process.
- configuration meta-model.

Configuration
#############

The package b3j0f.conf.model provides Configuration class in order to inject configuration resources in a configurable class.

Configuration resources respect two levels of configuration same as the ini configuration model. Both levels are respectively:

- Category: permits to define a set of parameters unique by name.
- Parameter: couple of property name and value.

And all categories/parameters are embedded in a Configuration class.

Configuration and Categories are ordered dictionaries where key values are inner element names. Therefore, Parameter names are unique per Categories, and Category/Parameter names are unique per Configuration.

Parameter Overriding
####################

In a dynamic and flexible way, one Configurable class can be bound to several Categories and Parameters. The choice is predetermined by the class itself. That means that one Configurable class can use several configuration resources and all/some/none Categories/Parameters in those resources. In such a way, the order is important because it permits to keep only last parameter values when parameters have the same name.

This overriding is respected by default with Configurable class inheritance. That means a sub class which adds a resource after its parent class resources indicates than all parameters in the final resources will override parameters in the parent class resources where names are the sames.

Name such as a regular expression
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Even if a parameter uses a name, it is possible to use this name such as a regular expression name.

In this case, while reading a configuration from a resource, all configuration parameters which match the regular expression will use the same attributes as defined in the parameter with the regular expression. And a name which is the name from the configuration resource.

Parser
~~~~~~

The package b3j0f.conf.parser provides parsers used to deserialize parameter values.

All parsers use special entries such as:

- %(lang:)expr%: string value of a programming language expression. ``lang`` is the target language (default is python) and ``expr`` is the expression to evaluate. For example, ``%"testy"[:-1]%`` equals ``test``.
- @((rpath/)cname.)[history]pname: reference to another parameter value (thanks to the idea from the pypi config_ project) where:

  - ``rpath``: optional resource path.
  - ``cname``: optional category name.
  - ``history``: optional parameter history in the arborescence from the (current) category. If not given, last parameter value is given.
  - ``pname``: parameter name.

  For example: ``@test`` designates the final value of the parameter ``test``. ``@myconf.json/test`` is the parameter ``test`` from the resource ``myconf.json``. ``@mycat...test`` is the parameter ``test`` defined two categories before the category ``mycat``.

If the parameter configuration value is of the format ``=(lang:)expr``, the result is an evaluation of ``expr`` in the given language ``lang``. For example, ``=2`` equals the integer 2. ``=sys.maxsize`` is the maxsize value from the sys module (thanks to the best effort property).

Finally, here are reserved keywords in an evaluated expression:

- ``conf``: current configuration.
- ``configurable``: current configurable.

.. note::

  By default, ``besteffort`` and ``safe`` properties are enabled. They respectively permit to resolve absolute object path and avoid to call I/O functions. They can be changed in the resperive Configurable, like the expression execution scope value which contains by default both configuration and ``configurable`` noted above.

Configurable
############

A Configurable class is provided in the b3j0f.conf.configurable.core module. It permits to get parameters from configuration resources and setup them to a python object or in a method/function parameters.

It inherits from the ``b3j0f.annotation.Annotation`` class (`annotation`_). That means it can be used such as an annotation (decorator with annotation functions). For example, bound Configurables to an object ``o`` are retrieved like this: ``Configurable.get_annotations(o)``.

In order to perform a configuration setup, it uses:

- conf: configuration model.
- drivers: configuration resource drivers.
- scope: parsing execution scope.
- besteffort: boolean flag which aims to resolve automatically absolute object path. True by default.
- safe: boolean flag which aims to cancel calls to I/O functions. True by default.
- logger: logger which will handle all warning/error messages. None by default.

Annotated elements are bound and can all be (re)configured once in using the method applyconfiguration.

Driver
######

Drivers are the mean to parse configuration resources, such as files, DB documents, etc. from a configuration model provided by a Configurable object.

By default, conf drivers are able to parse json/ini/xml files. Those last use a relative path given by the environment variable ``B3J0F_CONF_DIR`` or from directories (in this order) ``/etc``, ``/usr/local/etc``, ``~/etc``, ``~/.config``, ``~/config``, current execution directory or absolute path.

Example
-------

Bind configuration files to an object
#####################################

Bind the configuration file ``~/etc/myobject.conf`` and ``~/.config/myobject.conf`` to a business class ``MyObject`` (the relative path ``~/etc`` can be changed thanks to the environment variable ``B3J0F_CONF_DIR``).

The configuration file contains a category named ``MYOBJECT`` containing the parameters:

- ``myattr`` equals ``'myvalue'``.
- ``six`` equals ``6``.
- ``twelve`` equals ``six * 2.0``.

Let the following configuration file ``~/etc/myobject.conf`` in ini format:

.. code-block:: ini

  [MYOBJECT]
  myattr = myvalue
  twelve = =@six * 2.0

Let the following configuration file ``~/.config/myobject.conf`` in json format:

.. code-block:: json

  {
    "MYOBJECT": {
      "six": 6
    }
  }

The following code permits to load upper configuration to a python object.

.. code-block:: python

  from b3j0f.conf import Configurable

  # instantiate a business class
  @Configurable(paths='myobject.conf')
  class MyObject(object):
      pass

  myobject = MyObject()

  # assert attributes
  assert myobject.myattr == 'myvalue'
  assert myobject.six == 6
  assert isinstance(myobject.six, int)
  assert myobject.twelve == 12
  assert isinstance(myobject.twelve, float)

The following code permits to load upper configuration to a python function.

.. code-block:: python

  from b3j0f.conf import Parameter, Array

  # instantiate a business class and ensure twelve is converted into an integer and a string with commas is converted into an array of integers.
  @Configurable(
    paths='myobject.conf',
    conf=[
      Parameter('default', value=len('default')),  # default value for the parameter default
      Parameter('twelve', ptype=int),
      Parameter('integers', svalue='1,2,3', ptype=Array(int))
  )
  def myfunc(myattr=None, six=None, twelve=None, default=None):  # Only None values will be setted by the configuration
      return myattr, six, twelve, default

  myattr, six, twelve, default = myfunc(twelve=46)

  # assert attributes
  assert myobject.default == 7
  assert myobject.myattr == 'myvalue'
  assert myobject.six == 6
  assert myobject.twelve == 46
  assert isinstance(myobject.twelve, int)
  assert myobject.integers == [1, 2, 3]

Class configuration
###################

.. code-block:: python

  from b3j0f.conf import category
  from b3j0f.conf import Configurable

  # class configuration
  @Configurable(conf=category('land', Parameter('country', value='fr')))
  class World(object):
      pass

  world = World()
  assert world.country == 'fr'

One configuration with several objects
######################################

.. code-block:: python

  land = Configurable.get_annotations(world)[0]  # class method for retrieving Configurables

  @land  # bind land to World2
  class World2(object):
      pass

  world2 = World2()

  assert World2().country == 'fr'

  class World3(object):
      pass

  world3 = World3()
  land.applyconfiguration([world3])  # apply land on world3 without annotated it

  assert world3.country == 'fr'

  world3s = (land(World3()) for _ in range(5))  # annotate a set of worlds

  land.conf['land']['country'] = 'en'  # change default country code

  land.applyconfiguration()  # update all annotated objects

  for _world3 in world3s:
      assert _world3.country == 'en'

  assert world2.country == 'en'

  assert world3.country == 'fr'  # check not annotated element has not changed

Configure object constructor
############################

.. code-block:: python

  land.autoconf = False  # disable autoconf

  @land
  class World4(object):
      def __init__(self, country=None):
          self.safecountry = country

  world4 = World4()

  assert not hasattr(world4, 'country')  # disabled auto conf side effect
  assert world4.safecountry = 'en'

  land.applyconfiguration()  # configure all land targets

  assert world4.country == 'en'

Configure function parameters
#############################

.. code-block:: python

  @land
  def getcountry(country=None):
      print(country)
      return country

  assert getcountry() == 'en'

  land['land']['country'] = 'fr'

  assert getcountry() == 'fr'

Configure embedded objects
##########################

.. code-block:: python

  from b3j0f.conf import configuration, category, Parameter

  class SubTest(object):
      pass

  @Configurable(
      conf=(
          configuration(
              category('', Parameter('subtest', value=SubTest)),
  # the prefix ':' refers (recursively) to a sub configuration for the parameter named with the suffix after ':'
              category(':subtest', Parameter('subsubtest', value=SubTest)),
              category(':subtset:subsubtest', Parameter('test', value=True))
          )
      )
  )
  class Test(object):
      pass

  test = Test()

  assert isinstance(test.subtest, SubTest)
  assert isinstance(test.subtest.subsubtest)
  assert not hasattr(test.subtest, 'test')
  assert test.subtest.subsubtest.test is True

  # and you can still apply configuration
  Configurable.get_annotations(test)[0].conf[':subtset:subsubtest']['test'] = False
  applyconfiguration(targets=[test])

  assert test.subtest.subsubtest.test is False

Configure metaclasses
#####################

.. code-block:: python

  from six import add_metaclass

  @Configurable(conf=Parameter('test', value=True))
  class MetaTest(type):
      pass

  @add_metaclass(MetaTest)
  class Test(object):
      pass

  test = Test()

  assert test.test is True

Perspectives
------------

- wait feedbacks during 6 months before passing it to a stable version.
- Cython implementation.
- add GUI in order to ease management of multi resources and categorized parameters.

Donation
--------

.. image:: https://liberapay.com/assets/widgets/donate.svg
   :target: https://liberapay.com/b3j0f/donate
   :alt: I'm grateful for gifts, but don't have a specific funding goal.

.. _Homepage: https://github.com/b3j0f/conf
.. _Documentation: http://b3j0fconf.readthedocs.org/en/master/
.. _PyPI: https://pypi.python.org/pypi/b3j0f.conf/
.. _config: https://pypi.python.org/pypi/config/
.. _annotation: https://github.com/b3j0f/annotation
