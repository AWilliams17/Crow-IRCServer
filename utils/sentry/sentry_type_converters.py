from .sentry_criteria import SentryCriteria

""" Predefined conversion objects. These will (attempt to) convert any values before they get set to the
appropriate config object's attribute. """


class StringRequired(SentryCriteria):
    @property
    def required_type(self):
        return str

    @property
    def type_error_message(self):
        return "This option must be a string."


class IntRequired(SentryCriteria):
    @property
    def required_type(self):
        return int

    @property
    def type_error_message(self):
        return "This option must be a number."


class BoolRequired(SentryCriteria):
    @property
    def required_type(self):
        return bool

    @property
    def type_error_message(self):
        return "This option must be a boolean."


class DictRequired(SentryCriteria):
    @property
    def required_type(self):

        def dict_maker(value):
            if ":" and "," in value:
                return dict(x.split(":") for x in value.split(','))
            raise ValueError("Bad conversion")

        return dict_maker

    @property
    def type_error_message(self):
        return "This option must be a dict EG: option = key:value, key2:value"


class ListRequired(SentryCriteria):
    @property
    def required_type(self):

        def list_maker(value):
            if ',' in value:
                return list(value.split(','))
            raise ValueError("Bad conversion")

        return list_maker

    @property
    def type_error_message(self):
        return "This option must be a list EG: option = [1, 2, 3]"
