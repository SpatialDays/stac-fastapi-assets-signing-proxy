from abc import abstractmethod


class SigningMiddleware:

    def __init__(self):
        pass

    @abstractmethod
    def sign_href(self, href):
        pass