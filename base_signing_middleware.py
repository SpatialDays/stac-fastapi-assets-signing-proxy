from abc import abstractmethod
from typing import Tuple

class SigningMiddleware:

    def __init__(self):
        pass

    @abstractmethod
    def sign_href(self, href) -> Tuple[str, bool]:
        pass