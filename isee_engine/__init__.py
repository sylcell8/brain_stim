
__version__ = '0.1.0'

class UnknownModelError(Exception):
    def __init__(self, requested_model_name):
        super(self.__class__, self).__init__('Requested model "%s" not defined' % requested_model_name)