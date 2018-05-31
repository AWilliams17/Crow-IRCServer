from abc import abstractmethod
from .sentry_exceptions import CriteriaNotMetError


class SentryCriteria:
    @abstractmethod
    def criteria(self, value):
        pass

    def __call__(self, option_name, value):
        result = self.criteria(value)
        if result is not None:
            raise CriteriaNotMetError(option_name, result)
        return True


class SentryCriteriaConverter:
    @property
    @abstractmethod
    def required_type(self):
        return str

    @property
    @abstractmethod
    def type_error_message(self):
        return ""

    def __call__(self, option_name, value):
        try:
            self.required_type(value)
        except ValueError:
            raise CriteriaNotMetError(option_name, self.type_error_message)
