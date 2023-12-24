#!/usr/bin/env python3

import os
import sys
import json

import dotenv
import stytch
from flask import Flask, render_template, request, url_for, session, redirect


# load the .env file
dotenv.load_dotenv()

# By default, run on localhost:3000
HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", "3000"))
MAGIC_LINK_URL = f"http://{HOST}:{PORT}/authenticate"

# Load the Stytch credentials, but quit if they aren't defined
STYTCH_PROJECT_ID = os.getenv("STYTCH_PROJECT_ID")
STYTCH_SECRET = os.getenv("STYTCH_SECRET")
if STYTCH_PROJECT_ID is None:
    sys.exit("STYTCH_PROJECT_ID env variable must be set before running")
if STYTCH_SECRET is None:
    sys.exit("STYTCH_SECRET env variable must be set before running")

# NOTE: Set environment to "live" if you want to hit the live api
stytch_client = stytch.Client(
    project_id=STYTCH_PROJECT_ID,
    secret=STYTCH_SECRET,
    environment="test",
)

# create a Flask web app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # You can replace this with your own secret key


# handles the homepage for Hello Socks
@app.route("/")
def index() -> str:
    return render_template("loginOrSignUp.html")


@app.route("/otp")
def otp() -> str:
    return render_template("otp.html")


@app.route("/send_otp", methods=["POST"])
def send_otp() -> str:
    resp = stytch_client.otps.sms.login_or_create(
        phone_number="+1" + request.form["phone"]
    )

    if resp.status_code != 200:
        print(resp)
        return "something went wrong sending OTP"
    json_obj = json.loads(resp.json())
    return render_template("otpSent.html", phone_id=json_obj["phone_id"])


@app.route("/verify_otp", methods=["POST"])
def verify_otp() -> str:
    resp = stytch_client.otps.authenticate(
        code=request.form["otp"],
        method_id=request.form["phone_id"]
    )

    if resp.status_code != 200:
        print(resp)
        return "something went wrong verifying OTP"
    session['logged_in'] = True
    return render_template("loggedIn.html")


# takes the email entered on the homepage and hits the stytch
# loginOrCreateUser endpoint to send the user a magic link
@app.route("/login_or_create_user", methods=["POST"])
def login_or_create_user() -> str:
    resp = stytch_client.magic_links.email.login_or_create(
        email=request.form["email"],
        login_magic_link_url=MAGIC_LINK_URL,
        signup_magic_link_url=MAGIC_LINK_URL,
    )

    if resp.status_code != 200:
        print(resp)
        return "something went wrong sending magic link"
    return render_template("emailSent.html")


# This is the endpoint the link in the magic link hits.
# It takes the token from the link's query params and hits the
# stytch authenticate endpoint to verify the token is valid
@app.route("/authenticate")
def authenticate() -> str:
    resp = stytch_client.magic_links.authenticate(request.args["token"])

    if resp.status_code != 200:
        print(resp)
        return "something went wrong authenticating token"
    session['logged_in'] = True
    return render_template("loggedIn.html")


# handles the logout endpoint
@app.route("/logout")
def logout() -> str:
    session.clear()
    return redirect(url_for('index'))


@app.route("/home")
def home() -> str:
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))
    return render_template("home.html")


@app.route("/register_device", methods=["POST"])
def register_device() -> str:
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))

    device_name = request.form["device_name"]
    # Add your device registration logic here
    return f"Device '{device_name}' has been registered for computation donation."



# run's the app on the provided host & port
if __name__ == "__main__":
    # in production you would want to make sure to disable debugging
    app.run(host=HOST, port=PORT, debug=True)
    app.add_url_rule("/otp", "otp", otp)
    app.add_url_rule("/send_otp", "send_otp", send_otp, methods=["POST"])
    app.add_url_rule("/verify_otp", "verify_otp", verify_otp, methods=["POST"])
