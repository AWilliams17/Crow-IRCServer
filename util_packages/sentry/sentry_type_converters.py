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
