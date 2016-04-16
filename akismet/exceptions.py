

class AkismetError(Exception):
    pass


class InternalPykismetError(AkismetError):
    pass


class MissingApiKeyError(AkismetError):
    pass


class MissingParameterError(AkismetError):
    pass


class ExtraParametersError(AkismetError):
    pass


class AkismetServerError(AkismetError):
    pass
