from abc import abstractmethod
from .sentry_exceptions import CriteriaNotMetError


class SentryCriteria:
    """ In order for a config value to be properly set, it must pass any and all checks defined in criteria. """
    @abstractmethod
    def criteria(self, value):
        pass

    def __call__(self, option_name, value):
        result = self.criteria(value)
        if result is not None:
            raise CriteriaNotMetError(option_name, result)
        return True


class SentryCriteriaConverter:
    """ For handling conversions of a value before the attribute in the config section is set. """
    @property
    @abstractmethod
    def required_type(self):
        return type

    @property
    @abstractmethod
    def type_error_message(self):
        return ""

    def __call__(self, option_name, value):
        try:
            self.required_type(value)
        except ValueError:
            raise CriteriaNotMetError(option_name, self.type_error_message)
