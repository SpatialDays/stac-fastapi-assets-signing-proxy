"""
This Flask app is meant to proxy requests to a stac-fastapi server.
The app intercepts the response and modifies the JSON data.
Additionally, it accepts any query parameters that might be specified in the request.

To facilitate easy interception, the app sets the 'Accept-Encoding' header to 'utf-8'.
"""

from flask import Flask, jsonify, request, make_response
# azure_middleware = AzureBlobSigningMiddleware(account_key="MQ453kCMoIsYE4MZhiAxpkQw18hL+Wr5vW4fF/2OfD/DlITcnFjqBJ8EXG/OzTo0hTO0kvwvjykJ+AStkLen8A==", account_name="oseoinfrastagingstrgacc")
from signing_dispacher import SigningDispatcher
import requests
import os


app = Flask(__name__)
_TARGET_STAC_FASTAPI_ENDPOINT = os.environ.get("TARGET_STAC_FASTAPI_ENDPOINT", "http://stac-fastapi.os-eo-platform-rg-staging.azure.com:80")
_PROXY_PORT = int(os.environ.get("PROXY_PORT", 8083))

@app.after_request
def modify_response(response):
    # check if the response is JSON
    if "application/json" in response.headers.get("Content-Type", "") or "application/geo+json" in response.headers.get("Content-Type", ""):
        # modify the response JSON
        json_data = response.json
        # create a new response with the modified JSON data
        # any request changing middleware should be added here
        signing_dispatcher = SigningDispatcher()
        json_data = signing_dispatcher.sign_all_assets(json_data)
        new_response = make_response(jsonify(json_data), response.status_code)
        new_response.headers = response.headers
        new_response.headers["Content-Length"] = len(new_response.data)
        return new_response
    return response


@app.route("/", methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def proxy_request(path=""):
    try:
        headers = request.headers
        _headers_to_pass = [
            "User-Agent",
            "Authorization",
            "Content-Type",
            "Cache-Control",
            "X-Forwarded-For",
            "Connection",
            "Forwarded",
            "X-Forwarded-For",
            "X-Forwarded-Host",
            "X-Forwarded-Proto",
        ]
        new_headers = {}
        for key, value in headers.items():
            if key in _headers_to_pass:
                new_headers[key] = value
        if "Forwarded" not in new_headers:
            host = headers.get("Host", None)
            if host is None:
                raise ValueError("Host header is missing")
            proto = headers.get("X-Forwarded-Proto", "http")
            new_headers["Forwarded"] = f"proto={proto};host={host}"

        new_headers["Accept-Encoding"] = "utf-8"
        # if _TARGET_STAC_FASTAPI_ENDPOINT end with a slash, remove it
        target_stac_fastapi_endpoint = _TARGET_STAC_FASTAPI_ENDPOINT # TODO: replace with some urllib
        if target_stac_fastapi_endpoint.endswith("/"):
            target_stac_fastapi_endpoint = target_stac_fastapi_endpoint[:-1]
        url = f"{target_stac_fastapi_endpoint}/{path}"
        method = request.method.lower()
        if method == "get":
            query_params = request.args
            if query_params:
                url += "?" + "&".join([f"{k}={v}" for k, v in query_params.items()])
            response = requests.get(url, headers=new_headers)
        elif method == "post":
            response = requests.post(url, headers=new_headers, data=request.data)
        response.raise_for_status()
        new_response = make_response(response.content, response.status_code)
        for key, value in response.headers.items():
            new_response.headers[key] = value
        return new_response

    except requests.exceptions.HTTPError as e:
        error_code = e.response.status_code
        error_message = str(e)
        return make_response(jsonify({"error": error_message}), error_code)

    except ValueError as e:
        error_code = 400
        error_message = str(e)
        return make_response(jsonify({"error": error_message}), error_code)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=_PROXY_PORT, debug=True)