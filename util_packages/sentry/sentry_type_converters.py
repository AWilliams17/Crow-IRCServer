from .sentry_criteria import SentryCriteriaTypeEnforcer


class StringRequired(SentryCriteriaTypeEnforcer):
    @property
    def required_type(self):
        return str

    @property
    def type_error_message(self):
        return "A string of text."
