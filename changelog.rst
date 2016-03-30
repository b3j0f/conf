ChangeLog
=========

0.3.4 (2016/03/30)
------------------

- simplify installation in using the package_data parameter in the setup.
- move etc to b3j0f/conf/data.

0.3.3 (2016/03/30)
------------------

- fix easy_install installation.

0.3.2 (2016/03/29)
------------------

- fix installation of the configuration files.

0.3.1 (2016/03/16)
------------------

- add support for recursive configuration of sub objects.
- simplify code.
- add the attribute keepstate which ensure sub objects are not reinstantiate if they already exist.

0.3.0 (2016/03/12)
------------------

- a Configurable inherits from an b3j0f.annotation.Annotation
- a configurable can inject configuration in function parameters.
- support xml files.
- add logger in Configurable.
- simplify the Logger configurable.
- support sub configuration.

0.2.5 (2016/02/20)
------------------

- fix installation via easy-install in adding the etc folder in the project.

0.2.4 (2016/01/11)
------------------

- add confpath parameter in order to import configurable configuration from a file.
- add ui package.

0.2.3 (2015/12/20)
------------------

- add support for python2.6.

0.2.2 (2015/12/16)
------------------

- add the function model.parser.serialize in order to easily serialiaze Param values.
- simplify driver API in order to make easier the development of new drivers.
- move the logging part from the Configurable class to the specific module configurable.logger.
- set inheritance to Configurable from b3j0f.annotation.PrivateCallInterceptor.
- remove decorator module.
- add foreigns attributes in Configurable which allows to add not specified parameters given by conf resources.
- add autoconf attribute in Configurable, getconfigurables and applyconfiguration functions.
- rename get_conf, set_conf, to_configure and apply_configuration to getconf, setconf, targets and applyconfiguration.
- add Configurable.safe attribute in order to execute configuration in an unsafe context if necessary.
- add the configurable Logger useful to ease management of complex logging needs.

0.2.1 (2015/10/29)
------------------

- add the module model.parser which contains all parser functions provided previously in the class Parameter.
- add serialized value in parameter.
- add the parser eval which evaluates a simple and safe python lambda body expression (without I/O functions).

0.2.0 (2015/10/28)
------------------

- simplify the global architecture in removing both module registry and ParamList.
- separate the module model to three dedicated modules: model.configuration, model.parameter, model.category.
- add model UTs.
- add parameter conf and type in Parameter in order to respectively set initialization parameter value with additional configuration data and force parameter type.
- add regex in parameter name.
- allow to configure parameter values which are configurables.
- add the property Parameter.error which equals an Exception if change of value fired an exception.
- add the module version in order to manage from one access point the project version number.

0.1.9 (2015/09/28)
------------------

- use b3j0f.utils.property.addproperties in order to reduce code lines.
- use the english date time format in the changelog file.

0.1.8 (2015/09/22)
------------------

- add reference to Configurable, ConfigurableRegistry, ConfDriver, Configuration, Category and Parameter in the main package.

0.1.7 (2015/07/22)
------------------

- fix bug about targets parameter.
- update README in fixing the example.

0.1.6 (2015/06/13)
------------------

- use the docs directory related to readthedocs requirements.

0.1.5 (2015/06/13)
------------------

- use shields.io badges in the README.

0.1.4 (2015/06/02)
------------------

- use B3J0F_CONF_DIR environment variable in order to get default FileConfDriver default path for given conf files. Otherwise, use '~/etc' path.

0.1.2 (2015/05/20)
----------------

- remove retrocompatibility with python2.6

0.1.1 (2015/05/20)
------------------

- add __all__ in modules and packages
- add base classes in packages
- fix UTs in all python versions but 2.6

0.1.0 (2015/05/20)
------------------

- commit first version with poor comments and documentation.
- watcher module does not work.
