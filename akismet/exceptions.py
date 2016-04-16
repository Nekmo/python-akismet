

class AkismetError(Exception):
    pass


class MissingParameterError(AkismetError, ValueError):
    pass


class AkismetServerError(AkismetError):
    pass
