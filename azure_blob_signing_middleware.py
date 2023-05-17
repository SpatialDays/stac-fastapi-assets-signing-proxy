from base_signing_middleware import SigningMiddleware
from datetime import datetime, timedelta
from urllib.parse import urlparse
from azure.storage.blob import generate_blob_sas, BlobSasPermissions


class AzureBlobSigningMiddleware(SigningMiddleware):
    def __init__(self, account_name, account_key,container_name):
        super().__init__()
        self.account_name = account_name
        self.account_key = account_key
        self.container_name = container_name
        self.sas_token_cache = {}

    def sign_href(self, href):
        return self.get_read_sas_token(href)

    def get_read_sas_token(self, blob_url):
        if blob_url in self.sas_token_cache:
            token, expiry = self.sas_token_cache[blob_url]
            if expiry > datetime.utcnow() + timedelta(minutes=5):
                return f"{blob_url}?{token}", True
            else:
                del self.sas_token_cache[blob_url]
        parsed_url = urlparse(blob_url)
        path = parsed_url.path[1:]  # Remove leading slash
        # The first part of the path is the container name
        container_name, _, blob_name = path.partition('/')
        account_name = parsed_url.netloc.split('.')[0]
        if account_name != self.account_name:
            # do not sign blobs that dont belong to the account
            return blob_url, False
        if container_name != self.container_name:
            # do not sign blobs that dont belong to the container
            return blob_url, False
        sas_token = generate_blob_sas(
            account_name=self.account_name,
            container_name=container_name,
            blob_name=blob_name,
            account_key=self.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=48)
        )
        self.sas_token_cache[blob_url] = (sas_token, datetime.utcnow() + timedelta(hours=48))
        return f"{blob_url}?{sas_token}", True

