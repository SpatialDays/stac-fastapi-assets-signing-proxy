import datetime
from urllib.parse import urlparse

import requests

from base_signing_middleware import SigningMiddleware


class MicrosoftPlanetarySigningMiddleware(SigningMiddleware):

    def __init__(self):
        super().__init__()
        self.token_cache = {}
        self.error_cache = {}

    def get_token_from_microsoft_blob(self, storage_account, container_name):
        if (storage_account, container_name) in self.token_cache:
            token, expiry_time = self.token_cache[(storage_account, container_name)]
            if expiry_time > datetime.datetime.utcnow():
                return token

        if (storage_account, container_name) in self.error_cache:
            raise Exception(
                f"Error getting token from Microsoft Planetary Computer for {storage_account}/{container_name}")

        try:
            url = f'https://planetarycomputer.microsoft.com/api/sas/v1/token/{storage_account}/{container_name}'
            r = requests.get(url)
            token_expiry_timestamp = datetime.datetime.strptime(r.json()['msft:expiry'], '%Y-%m-%dT%H:%M:%SZ')
            token = r.json()['token']
            expiry_time = token_expiry_timestamp - datetime.timedelta(minutes=5)
            self.token_cache[(storage_account, container_name)] = (token, expiry_time)
            return token
        except:
            self.error_cache[(storage_account, container_name)] = True
            raise Exception(
                f"Error getting token from Microsoft Planetary Computer for {storage_account}/{container_name}")

    def sign_href(self, href):
        return self.get_read_sas_token(href)

    def get_read_sas_token(self, blob_url):
        parsed_url = urlparse(blob_url)
        path = parsed_url.path[1:]  # Remove leading slash
        # The first part of the path is the container name
        container_name, _, blob_name = path.partition('/')
        account_name = parsed_url.netloc.split('.')[0]
        try:
            token = self.get_token_from_microsoft_blob(account_name, container_name)
            return f"{blob_url}?{token}"
        except Exception as e:
            return blob_url
