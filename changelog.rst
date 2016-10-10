ChangeLog
=========

0.3.21 (2016/10/05)
-------------------

- fix default serialized value.

0.3.21 (2016/10/05)
-------------------

- add an error message when using the Array object with a wrong item type.
- fix default svalue/value for param.

0.3.20 (2016/09/03)
-------------------

- improve support of specific parser.

0.3.19 (2016/09/02)
-------------------

- fix support of specific parser.

0.3.18 (2016/06/06)
-------------------

- fix support of python3.4 with old style class.

0.3.17 (2016/06/05)
-------------------

- fix support of python3.4.

0.3.16 (2016/06/05)
-------------------

- fix reloading of modules.
- add the parameter modules in all configurable methods in order to load modules before use it.
- add the parameter rel for forcing configurable module reloading. Default is False.

0.3.15 (2016/06/02)
-------------------

- fix compatibility with python>3.4.

0.3.14 (2016/04/10)
-------------------

- Add support for default parameters automatically set in the configuration.

0.3.13 (2016/04/10)
-------------------

- Add item type in the Array class.

0.3.12 (2016/04/10)
-------------------

- save Configurable modules such as a list of modules and not a list of string.

0.3.11 (2016/04/05)
-------------------

- add user/absolute path in file driver.
- avoid to set parameters when already given in constructor parameters.

0.3.10 (2016/04/05)
-------------------

- fix UTs and subconfiguration.

0.3.9 (2016/04/03)
------------------

- improve the API in authorizing the use of Configuration, Category or Parameter when a configuration is requested.
- fix a bug when calling the applyconfiguration function with inheritance requirements between the default conf and a new conf.

0.3.8 (2016/04/02)
------------------

- add BOOL and ARRAY parameter type converters.
- fix parameter conversion from ptype.

0.3.7 (2016/04/02)
------------------

- add support of inheritance in updating model elements and get params from configuration.
- remove cleaned parameter in the methods ModelElement.copy and ModelElement.update.

0.3.6 (2016/04/02)
------------------

- fix bug while updating parameter ptype (new None values did change old consistent values).

0.3.5 (2016/04/02)
------------------

- fix bug while intercepting a configured object instanciation without resource reading.

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
