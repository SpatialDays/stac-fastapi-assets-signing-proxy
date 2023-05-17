from abc import abstractmethod
from typing import Tuple

class SigningMiddleware:

    def __init__(self):
        pass

    @abstractmethod
    def sign_href(self, href) -> Tuple[str, bool]:
        # Abstract method to be implemented by every signing middleware.
        # This method should return the URL and a boolean indicating if the URL was signed or not.
        # If the URL was not signed, the URL should be returned as is with the boolean set to False.
        # If the URL was signed, hence changed, the new URL should be returned with the boolean set to True.
        pass