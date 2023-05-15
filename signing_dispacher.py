import os

from azure_blob_signing_middleware import AzureBlobSigningMiddleware
from microsoft_planetary_computer_middleware import MicrosoftPlanetarySigningMiddleware

AZURE_BLOB_SIGNING_MIDDLEWARE_1_ACCOUNT_NAME = os.getenv("AZURE_BLOB_SIGNING_MIDDLEWARE_1_ACCOUNT_NAME")
AZURE_BLOB_SIGNING_MIDDLEWARE_1_ACCOUNT_KEY = os.getenv("AZURE_BLOB_SIGNING_MIDDLEWARE_1_ACCOUNT_KEY")
AZURE_BLOB_SIGNING_MIDDLEWARE_1_CONTAINER_NAME = os.getenv("AZURE_BLOB_SIGNING_MIDDLEWARE_1_CONTAINER_NAME")

azure_blob_signing_middleware = AzureBlobSigningMiddleware(account_name=AZURE_BLOB_SIGNING_MIDDLEWARE_1_ACCOUNT_NAME,
                                                           account_key=AZURE_BLOB_SIGNING_MIDDLEWARE_1_ACCOUNT_KEY,
                                                           container_name=AZURE_BLOB_SIGNING_MIDDLEWARE_1_CONTAINER_NAME)
microsoft_planetary_signing_middleware = MicrosoftPlanetarySigningMiddleware()
_list_of_middleware = [azure_blob_signing_middleware, microsoft_planetary_signing_middleware]


class SigningDispatcher:
    def __init__(self):
        self.signed_urls = []

    def is_item_previously_signed(self, url):
        is_signed = False
        for signed_url in self.signed_urls:
            if signed_url in url:
                is_signed = True
                break
        return is_signed

    def sign_all_assets(self, data):
        def change_href(json_data):
            if isinstance(json_data, dict):
                for key, value in json_data.items():
                    if key == "href":
                        if not self.is_item_previously_signed(value):
                            signed_url = self.sign_href(value)
                            json_data[key] = signed_url
                            self.signed_urls.append(signed_url)
                    elif key == "links":
                        continue  # skip processing "links" key
                    else:
                        change_href(value)
            elif isinstance(json_data, list):
                for item in json_data:
                    change_href(item)
            return json_data

        new_data = change_href(data)
        return new_data

    def sign_href(self, href):

        for middleware in _list_of_middleware:
            # print(f"Signing {href} with {middleware.__class__.__name__}")
            href = middleware.sign_href(href)
        return href
