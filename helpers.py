
import requests

from flask import redirect, render_template, session
from functools import wraps


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def username_check(username):
    for letters in username:
        if letters.isspace():
            return "space"

    if len(username) < 3:
        return "length"

    return username


def password_check(password):
    letter = 0
    capital = 0
    for char in password:
        if char.isspace():
            return "space"
        if char.isalpha():
            letter += 1
        if char.isupper():
            capital += 1

    if letter < 2 or capital < 1 or len(password) < 6:
         return "format"

    return password


def aud(value):
    return f"${value:,.2f}"

def token_rounding(value):
    return f"{value:,.8f}"


def lookup(symbol):
    EXCHANGE_RATE = 1.53
    # defining key/request url
    if symbol == None:
        return False
    symbol = symbol.upper()+"USDT"
    key = "https://api.binance.com/api/v3/ticker/price?symbol="+symbol

    # requesting data from url
    data = requests.get(key)
    if data.status_code == 400:
        return False
    else:
        data = data.json()
        return {"price": float(data['price'])*EXCHANGE_RATE, "symbol": data['symbol'].replace("USDT","")}
