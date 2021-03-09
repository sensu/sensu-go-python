# Copyright (c) 2020 XLAB Steampunk


class SensuError(Exception):
    """ Base exception for the sensu-go package. """


class HTTPError(SensuError):
    """ Error that indicates a problem with backend connection. """


class ResponseError(SensuError):
    """ Error that indicates a problem with backend's response. """

    def __init__(self, msg: str, url: str, status: int, text: str) -> None:
        self.url = url
        self.status = status
        self.text = text

        super().__init__(
            "{}:\n  url: {}\n  status: {}\n  text: {}".format(msg, url, status, text)
        )


class AuthError(ResponseError):
    """ Error that indicates a problem with credentials. """
