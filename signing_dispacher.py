import os
import json
from dotenv import load_dotenv
import logging
logging.basicConfig(level=logging.INFO)

load_dotenv()

from typing import Tuple
from azure_blob_signing_middleware import AzureBlobSigningMiddleware
from microsoft_planetary_computer_middleware import MicrosoftPlanetarySigningMiddleware

_AZURE_BLOB_SIGNING_MIDDLEWARE_CONFIG_PATH = os.getenv("AZURE_BLOB_SIGNING_MIDDLEWARE_CONFIG_PATH")

microsoft_planetary_signing_middleware = MicrosoftPlanetarySigningMiddleware()
_list_of_middleware = [microsoft_planetary_signing_middleware]

# open a json file
with open(_AZURE_BLOB_SIGNING_MIDDLEWARE_CONFIG_PATH) as json_file:
    data = json.load(json_file)
    for item in data:
        account_name = item["account_name"]
        container_name = item["container_name"]
        account_key = item["account_key"]
        azure_blob_signing_middleware = AzureBlobSigningMiddleware(account_name=account_name,
                                                                   account_key=account_key,
                                                                   container_name=container_name)
        _list_of_middleware.append(azure_blob_signing_middleware)

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
                            signed_url, signed = self.sign_href(value)
                            if signed:
                                json_data[key] = signed_url
                                # print(f"Adding URL to signed_urls: {signed_url}")
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

    def sign_href(self, href) -> Tuple[str, bool]:

        for middleware in _list_of_middleware:
            href, signed = middleware.sign_href(href)
            if signed:
                # print(f"Signing {href} with {middleware.__class__.__name__}")
                return href, signed
        return href,signed
