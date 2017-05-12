from functools import wraps


def list_required(func):
	@wraps(func)
	def wrapper(self, doc, *args, **kwargs):
		if isinstance(doc, list):
			return func(self, doc, *args, **kwargs)
		else:
			raise TypeError('Invalid argument passed to %s' % func.__name__)
	return wrapper
