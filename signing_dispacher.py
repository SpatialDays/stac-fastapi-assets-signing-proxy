from azure_blob_signing_middleware import AzureBlobSigningMiddleware
from microsoft_planetary_computer_middleware import MicrosoftPlanetarySigningMiddleware
azure_blob_signing_middleware = AzureBlobSigningMiddleware(account_name="", account_key= "", container_name="")
microsoft_planetary_signing_middleware = MicrosoftPlanetarySigningMiddleware()
_list_of_middleware = [azure_blob_signing_middleware, microsoft_planetary_signing_middleware]

class SigningDispatcher:
    def __init__(self):
        self.signed_urls = []

    def is_item_previous_signed(self, url):
        is_signed = False
        for signed_url in self.signed_urls:
            if signed_url in url:
                is_signed = True
                break
        return is_signed

    def sign_all_assets(self, data):
        def change_href(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == "href":
                        if not self.is_item_previous_signed(value):
                            signed_url = self.sign_href(value)
                            data[key] = signed_url
                            self.signed_urls.append(signed_url)   
                    elif key == "links":
                        continue  # skip processing "links" key
                    else:
                        change_href(value)
            elif isinstance(data, list):
                for item in data:
                    change_href(item)
            return data

        new_data = change_href(data)
        return new_data
    
    def sign_href(self, href):

        for middleware in _list_of_middleware:
            # print(f"Signing {href} with {middleware.__class__.__name__}")
            href = middleware.sign_href(href)
        return href
