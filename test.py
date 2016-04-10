from b3j0f.conf import Configurable, Parameter

configurable = Configurable(conf=[Parameter('test', value=2), Parameter('testy', value=3)])

@configurable
class Test(object):
	def __init__(self, test=None):
		self.testu = test

test = Test()

assert test.testu == 2
assert test.testy == 3
assert not hasattr(test, 'test')

_ = configurable.applyconfiguration(conf=Parameter('test', value=3))

assert test.test == 3