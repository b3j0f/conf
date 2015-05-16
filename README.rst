Description
-----------

Common tools useful to python projects.

.. image:: https://pypip.in/license/b3j0f.conf/badge.svg
   :target: https://pypi.python.org/pypi/b3j0f.conf/
   :alt: License

.. image:: https://pypip.in/status/b3j0f.conf/badge.svg
   :target: https://pypi.python.org/pypi/b3j0f.conf/
   :alt: Development Status

.. image:: https://pypip.in/version/b3j0f.conf/badge.svg?text=version
   :target: https://pypi.python.org/pypi/b3j0f.conf/
   :alt: Latest release

.. image:: https://pypip.in/py_versions/b3j0f.conf/badge.svg
   :target: https://pypi.python.org/pypi/b3j0f.conf/
   :alt: Supported Python versions

.. image:: https://pypip.in/implementation/b3j0f.conf/badge.svg
   :target: https://pypi.python.org/pypi/b3j0f.conf/
   :alt: Supported Python implementations

.. image:: https://pypip.in/format/b3j0f.conf/badge.svg
   :target: https://pypi.python.org/pypi/b3j0f.conf/
   :alt: Download format

.. image:: https://travis-ci.org/b3j0f/conf.svg?branch=master
   :target: https://travis-ci.org/b3j0f/conf
   :alt: Build status

.. image:: https://coveralls.io/repos/b3j0f/conf/badge.png
   :target: https://coveralls.io/r/b3j0f/conf
   :alt: Code test coverage

.. image:: https://pypip.in/download/b3j0f.conf/badge.svg?period=month
   :target: https://pypi.python.org/pypi/b3j0f.conf/
   :alt: Downloads

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

This library provides a set of class configuration tools in order to ease development of systems based on configuration resources such as files, DB documents, etc.

The main class is b3j0f.conf.configurable

Configurable classes are provided in order to be synced with configuration resources which respect two levels and are agnostic from configuration languages.

Both levels respect the first known configuration format which is ini.

Therefore, you may define a category which is associated to options.

A configurable can be bound to a several categories, which contain several options such as couple of property name and value.

- chaining: chain object methods calls in a dedicated Chaining object. Such method calls return the Chaining object itself, allowing multiple calls to object methods to be invoked in a concise statement.
- iterable: tools in order to manage iterable elements.
- path: python object path resolver, from object to absolute/relative path or the inverse.
- property: (un)bind/find properties in reflective and oop concerns.
- reflect: tools which ease development with reflective concerns.
- runtime: ease runtime execution.
- proxy: create proxy (from design pattern) objects from a routine or an object which respects the signature and description of the proxified element.
- ut: improve unit tests.
- version: ease compatibility between python version (from 2.x to 3.x).

Examples
--------

Perspectives
------------

- wait feedbacks during 6 months before passing it to a stable version.
- Cython implementation.

ChangeLog
---------

Donation
--------

.. image:: https://cdn.rawgit.com/gratipay/gratipay-badge/2.3.0/dist/gratipay.png
   :target: https://gratipay.com/b3j0f/
   :alt: I'm grateful for gifts, but don't have a specific funding goal.

.. _Homepage: https://github.com/b3j0f/conf
.. _Documentation: http://pythonhosted.org/b3j0f.conf
.. _PyPI: https://pypi.python.org/pypi/b3j0f.conf/
