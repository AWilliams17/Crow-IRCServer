#  is this bad practice?
class MissingOptionError(Exception):
    def __init__(self, section, option):
        message = "Section class {} has no option named {}".format(section, option)
        super().__init__(message)


class CriteriaDescriptionError(Exception):
    def __init__(self):
        message = "An option can not have criteria to meet without describing what that criteria is."
        super().__init__(message)


class CriteriaNotMetError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class NoDefaultGivenError(Exception):
    def __init__(self, section, option):
        message = "The option {} in section class {} has not been set nor does it have a default value.".format(section, option)
        super().__init__(message)

