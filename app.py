import os
import datetime
import cs50


from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, password_check, username_check, aud, lookup, token_rounding

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///account.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            return render_template("register.html", blank = True)


        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        #Basic username and password requirements
        if username_check(username) == "space" or username_check(password) == "space":
            return render_template("register.html", space = True)
        if username_check(username) == "length":
            return render_template("register.html", length_username = True)

        if password_check(password) == "format":
            return render_template("register.html", format = True)


        username_list = db.execute("SELECT username FROM users")
        for taken in username_list:
            if taken["username"] == username:
                return render_template("register.html", taken_name = True)

        if password != confirmation:
            return render_template("register.html", mismatch = True)

        password_hash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, password_hash)


        return render_template("register.html", success=True)

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username and password was submitted
        if not request.form.get("username") or not request.form.get("password"):
            return render_template("login.html", blank = True)


        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return render_template("login.html", invalid = True)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/")
@login_required
def index():
    balance = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    tokens = db.execute("SELECT symbol, AVG(price) AS price, SUM(token) AS token, SUM(total) AS total FROM assets WHERE user_id = ? GROUP BY symbol", session["user_id"])
    display = []
    for check in tokens:
        if check["total"] > 0:
            display.append(check)
    for bought in display:
        bought["price"] = aud(bought["price"])
        bought["total"] = aud(bought["total"])
        bought["token"] = token_rounding(bought["token"])
    return render_template("home.html", balance = aud(balance[0]["cash"]), display = display)



@app.route("/trade", methods=["GET", "POST"])
@login_required
def trade():
    balance = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"] )
    tokens = db.execute("SELECT symbol, SUM(total) AS total FROM assets WHERE user_id = ? GROUP BY symbol", session["user_id"])
    display = []
    for check in tokens:
        if check["total"] > 0:
            display.append(check)

    if request.method == "POST":
        if not request.form.get("amount"):
            return render_template("trade.html", blank = True, balance = aud(balance[0]["cash"]), display = display)

        symbol = request.form.get("symbol")
        amount = float(request.form.get("amount"))
        info = lookup(symbol)

        #Check for valid crypto symbol
        if symbol != None:
            if info == False:
                return render_template("trade.html", invalid = True, balance = aud(balance[0]["cash"]), display = display)

        trans_type = request.form.get("type")

        if trans_type == "buy":
            TYPE = "Buy"
            cash = balance[0]["cash"] - amount
            if cash < 0:
                return render_template("trade.html", insufficient_buy = True, balance = aud(balance[0]["cash"]), display = display)

            db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, session["user_id"])
            db.execute("INSERT INTO assets (user_id, symbol, price, token, total, type) VALUES (?, ?, ?, ?, ?, ?)",
                       session["user_id"], info["symbol"], info["price"], (amount / info["price"]), amount, TYPE)


        if trans_type == "sell":
            TYPE = "Sell"
            current_holding = db.execute("SELECT SUM(total) AS total FROM assets WHERE user_id = ? AND symbol = ?", session["user_id"], symbol)
            if current_holding[0]["total"] - amount < 0:
                return render_template("trade.html", insufficient_sell = True, balance = aud(balance[0]["cash"]), display = display)

            db.execute("UPDATE users SET cash = ? WHERE id = ?", balance[0]["cash"] + amount, session["user_id"])
            db.execute("INSERT INTO assets (user_id, symbol, price, token, total, type) VALUES (?, ?, ?, ?, ?, ?)",
                       session["user_id"], info["symbol"], info["price"], -(amount / info["price"]), -amount, TYPE)


        if trans_type == "deposit":
            db.execute("UPDATE users SET cash = ? WHERE id = ?", balance[0]["cash"] + amount, session["user_id"])


        if trans_type == "withdraw":
            if balance[0]["cash"] - amount < 0:
                return render_template("trade.html", insufficient_withdraw = True, balance = aud(balance[0]["cash"]), display = display)
            db.execute("UPDATE users SET cash = ? WHERE id = ?", balance[0]["cash"] - amount, session["user_id"])


        return redirect("/trade")


    else:
        return render_template("trade.html", balance = aud(balance[0]["cash"]), display = display)



@app.route("/watchlist", methods=["GET", "POST"])
@login_required
def watchlist():

    display = db.execute("SELECT * FROM watchlist WHERE id = ?", session["user_id"])
    for bought in display:
        bought["price"] = aud(bought["price"])

    if request.method == "POST":
        if not request.form.get("symbol"):
            return render_template("watchlist.html", blank = True, display = display)

        symbol = request.form.get("symbol")
        info = lookup(symbol)
        if info == False:
            return render_template("watchlist.html", invalid = True, display = display)

        dupe_check = db.execute("SELECT symbol FROM watchlist WHERE symbol = ? AND id = ?", info["symbol"], session["user_id"])
        if dupe_check != []:
            return render_template("watchlist.html", dupe = True, display = display)

        x = datetime.datetime.now()
        time = x.strftime("%x") + ", " + x.strftime("%X")
        db.execute("INSERT INTO watchlist (time, symbol, price, id) VALUES (?, ?, ?, ?)", time, info["symbol"], info["price"], session["user_id"])

        display = db.execute("SELECT * FROM watchlist WHERE id = ?", session["user_id"])
        for bought in display:
            bought["price"] = aud(bought["price"])

        return render_template("watchlist.html", display = display)

    else:
        return render_template("watchlist.html", display = display)

@app.route("/remove", methods=["GET", "POST"])
@login_required
def remove():
    remove = request.form.get("remove")
    if remove:
        info = lookup(remove)
        db.execute("DELETE FROM watchlist WHERE symbol = ? AND id = ?", info["symbol"], session["user_id"])

    return redirect("/watchlist")


@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    update = request.form.get("update")
    if update:
        info = lookup(update)
        x = datetime.datetime.now()
        time = x.strftime("%x") + ", " + x.strftime("%X")
        db.execute("UPDATE watchlist SET time = ?, price = ? WHERE symbol = ? AND id = ?", time, info["price"], info["symbol"], session["user_id"])

    return redirect("/watchlist")



@app.route("/history")
@login_required
def history():
    history = db.execute("SELECT symbol, token, price, total, type FROM assets WHERE user_id = ?", session["user_id"])
    for bought in history:
        bought["price"] = aud(bought["price"])
        bought["total"] = aud(bought["total"])
        bought["token"] = token_rounding(bought["token"])
    return render_template("history.html", history = history)
