from sentry.sentry_exceptions import CriteriaNotMetError, CriteriaDescriptionError


class SentryCriteria:
    """ This class represents the criteria a value must follow in order to be considered valid. Also has code to allow
    for the conversion of passed values. A derived class of SentryCriteria can either only do criteria checks, only
    do conversions of the value, or can do both. """
    def criteria(self, value):
        """
        This method, if overridden, should contain if statements against the value to validate.
        If any of the if statements fail, a string describing the condition which failed should be returned.
        Args:
            value: The value to validate.
        Returns: A string in the case of failing to validate describing why it wasn't valid.
        """
        pass

    @property
    def required_type(self):
        """ If overridden, the type returned here should be the type that is to be used to convert the option value. """
        return type

    @property
    def type_error_message(self):
        """ If overridden, the return value should be a string describing what type is required. Note that if
        required_type is overridden and the value fails to convert and this method is not overridden, then an
        exception of type CriteriaNotMetError will be raised. """
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
        """
        When called, this will either convert the option value to the specified type (if required_type is not type),
        run the value through criteria checks and raise a CriteriaNotMetError in the event of an error string being
        returned, or will do both of these things, with the conversion preceding the criteria checks.
        Args:
            option_name: The name of the option being validated. For use in the exception.
            value: The option value being converted/validated.

        Returns: None, or the converted value.
        """
        value_converted = False
        if self.required_type is not type:
            value = self.convert(option_name, value)
            value_converted = True

        failed_criteria_message = self.criteria(value)
        if failed_criteria_message is not None:
            raise CriteriaNotMetError(option_name, failed_criteria_message)

        if value_converted:
            return value
