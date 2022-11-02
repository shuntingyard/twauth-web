# twauth-web

A simple Python + FastAPI web app that demonstrates the flow of obtaining a [Twitter user OAuth access token](https://developer.twitter.com/en/docs/basics/authentication/overview/oauth).

## Setup

1. Obtain consumer key and secret from the Twitter Developer portal. The app should be configured to enable Sign in with Twitter. See `twauth-web.py` for more details, but you can either:
   1. add these values to a `.env` file (local deployment); or
   2. set environment variables `APP_CONSUMER_KEY` and `APP_CONSUMER_SECRET` (cloud deployment)
2. Setup a Python3 virtual environment, and install dependencies:
   1. `python -m venv venv`
   2. `. venv/bin/activate`
   3. `pip install -r requirements.txt`
3. Start the app:
   1. `hypercorn --certfile cert.pem --keyfile key.pem --bind example.com:8443 twauth-web:app`

> Note: the app must have an Internet-accessible URL - do not attempt to connect via localhost, as this will not work. You can run a tunnel e.g. `ngrok` for local use.

Open a browser window on your demo app's external URL. Don't click the buttons yet!

Finally, revisit the dev portal, and add your app's callback URL (`https://your-deployed-url/callback`) to the callback URL whitelist setting. Once saved, follow the instructions on the app's web UI to click through the demo pages.

## Reference

[Twitter Developer Portal](https://developer.twitter.com/)  
[Flask](https://flask.pocoo.org/)  
[python-oauth2](https://github.com/simplegeo/python-oauth2)  
[Bootstrap](https://getbootstrap.com/)  

### Credits

Original version by Jacob Petrie  
https://twitter.com/jaakkosf  
https://github.com/jaakko-sf/twauth-web  
https://github.com/shuntingyard/twauth-web for `FastAPI` integration

## TODO
- [x] check in your changes and create your own repo
- [ ] tidy up html stuff (external dependencies (fonts!) and format)
- [ ] make html stuff multilingual (using language prefs from user agent)
- [ ] persist access token using some kind of vault

## Related (Authlib)
[FastAPI Authlib examples](https://docs.authlib.org/en/latest/client/fastapi.html)  
[Lukasthaler FastAPI Oauth Examples](https://github.com/lukasthaler/fastapi-oauth-examples)
