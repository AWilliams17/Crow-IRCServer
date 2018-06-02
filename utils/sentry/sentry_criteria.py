from abc import abstractmethod
from .sentry_exceptions import CriteriaNotMetError, CriteriaDescriptionError


class SentryCriteria:
    """ In order for a config value to be properly set, it must pass any and all checks defined in criteria by way of
    if statements. The return value only should be a string which explains why the check failed. Otherwise, don't
    return anything. """
    @abstractmethod
    def criteria(self, value):
        pass

    @property
    def required_type(self):
        return type

    @property
    def type_error_message(self):
        return ""

    def convert(self, option_name, value):
        try:
            value = self.required_type(value)
            return value
        except ValueError:
            if self.type_error_message == "":
                raise CriteriaDescriptionError(option_name)
            raise CriteriaNotMetError(option_name, self.type_error_message)

    def __call__(self, option_name, value):
        value_converted = False
        if self.required_type is not type:
            value = self.convert(option_name, value)
            value_converted = True

        failed_criteria_message = self.criteria(value)
        if failed_criteria_message is not None:
            raise CriteriaNotMetError(option_name, failed_criteria_message)

        if value_converted:
            return value


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
