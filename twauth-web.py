import json
import os
from typing import Union
import urllib.parse

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import oauth2 as oauth

app = FastAPI()
templates = Jinja2Templates(directory="templates")

load_dotenv(".env")

REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"
AUTHORIZE_URL = "https://api.twitter.com/oauth/authorize"
SHOW_USER_URL = "https://api.twitter.com/1.1/users/show.json"

# add your key and secret to config.cfg
# config.cfg should look like:
# APP_CONSUMER_KEY = 'API_Key_from_Twitter'
# APP_CONSUMER_SECRET = 'API_Secret_from_Twitter'

oauth_store = {}


@app.get("/", response_class=HTMLResponse)
async def hello(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/start", response_class=HTMLResponse)
async def start(request: Request):
    # note that the external callback URL must be added to the whitelist on
    # the developer.twitter.com portal, inside the app settings
    app_callback_url = request.url_for("callback")

    # Generate the OAuth request tokens, then display them
    consumer = oauth.Consumer(
        os.getenv("APP_CONSUMER_KEY"), os.getenv("APP_CONSUMER_SECRET")
    )
    client = oauth.Client(consumer)
    resp, content = client.request(
        REQUEST_TOKEN_URL,
        "POST",
        body=urllib.parse.urlencode({"oauth_callback": app_callback_url}),
    )

    if resp["status"] != "200":
        error_message = (
            f"Invalid response, status {resp['status']}, "
            + f"{content.decode('utf-8')}"
        )
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error_message": error_message},
            status_code=int(resp["status"]),
        )

    request_token = dict(urllib.parse.parse_qsl(content))
    oauth_token = request_token[b"oauth_token"].decode("utf-8")
    oauth_token_secret = request_token[b"oauth_token_secret"].decode("utf-8")

    oauth_store[oauth_token] = oauth_token_secret
    return templates.TemplateResponse(
        "start.html",
        {
            "request": request,
            "authorize_url": AUTHORIZE_URL,
            "oauth_token": oauth_token,
            "request_token_url": REQUEST_TOKEN_URL,
        },
    )


@app.get("/callback", response_class=HTMLResponse)
async def callback(
    request: Request,
    oauth_token: Union[str, None] = None,
    oauth_verifier: Union[str, None] = None,
    denied: Union[str, None] = None,
):
    # Accept the callback params, get the token and call the API to
    # display the logged-in user's name and handle
    # oauth_token = request.get("oauth_token")
    # oauth_verifier = request.get("oauth_verifier")
    oauth_denied = denied

    # if the OAuth request was denied, delete our local token
    # and show an error message
    if oauth_denied:
        if oauth_denied in oauth_store:
            del oauth_store[oauth_denied]
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": "the OAuth request was denied by this user",
            },
        )  # TODO: status code

    if not oauth_token or not oauth_verifier:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error_message": "callback param(s) missing"},
        )  # TODO: status code

    # unless oauth_token is still stored locally, return error
    if oauth_token not in oauth_store:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": "oauth_token not found locally",
            },
        )  # TODO: status code

    oauth_token_secret = oauth_store[oauth_token]

    # if we got this far, we have both callback params and we have
    # found this token locally

    consumer = oauth.Consumer(
        os.getenv("APP_CONSUMER_KEY"), os.getenv("APP_CONSUMER_SECRET")
    )
    token = oauth.Token(oauth_token, oauth_token_secret)
    token.set_verifier(oauth_verifier)
    client = oauth.Client(consumer, token)

    resp, content = client.request(ACCESS_TOKEN_URL, "POST")
    access_token = dict(urllib.parse.parse_qsl(content))

    screen_name = access_token[b"screen_name"].decode("utf-8")
    user_id = access_token[b"user_id"].decode("utf-8")

    # These are the tokens you would store long term, someplace safe
    real_oauth_token = access_token[b"oauth_token"].decode("utf-8")
    real_oauth_token_secret = access_token[b"oauth_token_secret"].decode(
        "utf-8"
    )

    # Call api.twitter.com/1.1/users/show.json?user_id={user_id}
    real_token = oauth.Token(real_oauth_token, real_oauth_token_secret)
    real_client = oauth.Client(consumer, real_token)
    real_resp, real_content = real_client.request(
        SHOW_USER_URL + "?user_id=" + user_id, "GET"
    )

    if real_resp["status"] != "200":
        error_message = (
            "Invalid response from Twitter API GET users/show: "
            + f"{real_resp['status']}"
        )
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error_message": error_message},
            status_code=int(real_resp["status"]),
        )

    response = json.loads(real_content.decode("utf-8"))

    friends_count = response["friends_count"]
    statuses_count = response["statuses_count"]
    followers_count = response["followers_count"]
    name = response["name"]

    # don't keep this token and secret in memory any longer
    del oauth_store[oauth_token]

    return templates.TemplateResponse(
        "callback-success.html",
        {
            "request": request,
            "screen_name": screen_name,
            "user_id": user_id,
            "name": name,
            "friends_count": friends_count,
            "statuses_count": statuses_count,
            "followers_count": followers_count,
            "access_token_url": ACCESS_TOKEN_URL,
        },
    )


@app.exception_handler(500)
async def internal_server_error(request: Request, b):
    print(b)
    return (
        templates.TemplateResponse(
            "error.html",
            {"request": request, "error_message": "uncaught exception"},
            status_code=500,
        ),
    )
