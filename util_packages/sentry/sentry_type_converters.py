from .sentry_criteria import SentryCriteriaConverter


class StringConverter(SentryCriteriaConverter):
    @property
    def required_type(self):
        return str

    @property
    def type_error_message(self):
        return "This option must be a text."


class IntConverter(SentryCriteriaConverter):
    @property
    def required_type(self):
        return int

    @property
    def type_error_message(self):
        return "This option must be a number."


class BoolConverter(SentryCriteriaConverter):
    @property
    def required_type(self):
        return bool

    @property
    def type_error_message(self):
        return "This option must be a boolean."


class DictConverter(SentryCriteriaConverter):
    @property
    def required_type(self):

        def dict_maker(value):
            if ":" and "," in value:
                return dict(x.split(":") for x in value.split(','))
            return None

        return dict_maker

    @property
    def type_error_message(self):
        return "This option must be a dict EG: option = key:value, key2:value"


class ListConverter(SentryCriteriaConverter):
    @property
    def required_type(self):

        def list_maker(value):
            if ',' in value:
                return list(value.split(','))
            return None

        return list_maker

    @property
    def type_error_message(self):
        return "This option must be a list EG: option = [1, 2, 3]"



