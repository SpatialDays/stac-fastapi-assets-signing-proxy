from base_signing_middleware import SigningMiddleware


class AzureBlobSigningMiddleware(SigningMiddleware):
    def __init__(self):
        super().__init__()

    def sign_href(self, href):
        return "do something with the href"