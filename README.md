# STAC-FastAPI-Assets-Signing-Proxy
Flask Middleware software which intercepts requests to the STAC-API and appends/changes the HREF keys for the assets to be a presigned URL. This allows for the STAC-API to be seamlessly used with assets stored in private storage buckets/accounts.

## Currently supported sigining middleware
- Microsoft Planetary Computer
- Microsoft Azure Storage Account for Blob Containers

## How to make a new signing middleware
Create a class inherinting BaseClassMiddleware and implement sign_href method
