import os
import sqlite3

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from json import loads

from helpers import apology, login_required, extract_month_year, extract_dates
from summary import email_summary


# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure SQLite database
db = SQL("sqlite:///system.db")
def isint(amount):
    try: 
        result = int(amount)
    except ValueError: 
        return False
    return True
def isfloat(amount):
    try: 
        result = float(amount)
    except ValueError: 
        return False
    return True

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    user_id = session["user_id"]
    user_date = db.execute("SELECT * FROM transactions WHERE person_id = ?", user_id)
    dates = []
    options = extract_month_year(dates)
    if len(options) == 0:
        return render_template("index.html", options=None, chosen_option=None)
    chosen_option = options[0]
    if request.method == "POST":
        chosen_option = request.form.get("selected_month")
        print(chosen_option)
    return render_template("login.html", options=options, chosen_option=chosen_option)
    
@app.route("/main", methods=["GET", "POST"])
@login_required
def main():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            render_template("add.html")
        elif action == "view":
            user_id = session["user_id"]
            user_date = db.execute("SELECT * FROM dates WHERE person_id = ?", user_id)
            dates = []
            counter = 0
            for date in user_date:
                counter += 1
                dates.append(
                    {
                        "id": counter,
                        "Meetings": date["meets"],
                        "Tasks": date["tasks"],
                    }
                )
            render_template("view.html", dates=dates)

@app.route("/view", methods=["GET", "POST"])
@login_required
def view():
    if request.method == "POST":
        return render_template("add.html")
    
@app.route("/add", methods=["GET", "POST"])
@login_required
def edit():
    user_id = session["user_id"]
    if request.method == "POST":
        date = request.form.get("date")
        meets = request.form.get("appt")
        tasks = request.form.get("task")
        db.execute("INSERT INTO dates (person_id, date, meets, tasks VALUES (?, ?, ?, ?)", user_id, date, meets, tasks)
        flash("Meeting/Task Added!", "success")
        return render_template("main.html")
    else:
        return render_template("add.html")
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return render_template("main.html")

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

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Missing username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Missing password", 400)

        # Ensure password and confirmation is correct
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Password don't match", 400)

        # Ensure username is not taken
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)
        )
        if len(rows) != 0:
            return apology("Username Taken", 400)

        # Add user information into db
        else:
            name = request.form.get("username")
            password = request.form.get("password")
            password_hashed = generate_password_hash(password)
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", name, password_hashed)

            # Remember which user has logged in
            rows = db.execute("SELECT * FROM users WHERE username = ?", name)
            session["user_id"] = rows[0]["id"]
            flash("Registered!", "success")
            return redirect("/")
    else:
        return render_template("register.html")
    
@app.route("/email", methods=["GET", "POST"])
@login_required
def summary():
    if request.method == "POST":
        email = request.form.get("email")
        print(email)
        response = email_summary(email)
        print(response, type(response))
        Subject = response["Subject"]
        Sender = response["Sender"]
        Recipients = response["Recipients"]
        Date_Time = response["Date_time"]
        Main_Purpose = response["Main_Purpose"]
        Key_Points = response["Key_Points_Discussed"]
        Deadlines = response["Action_Items_and_Deadlines"]
        Attachments_Links = response["Attachments_Links"]
        Overall_Tone = response["Overall_Tone"]
        Summary = response["Summary"]
        
        return render_template("email.html", response=True, Subject=Subject, Sender=Sender, Recipients=Recipients, Date_Time=Date_Time, Main_Purpose=Main_Purpose,
                               Key_Points=Key_Points, Deadlines=Deadlines, Attachments_Links=Attachments_Links, Overall_Tone=Overall_Tone, Summary=Summary)
    else:
        return render_template("email.html", response=None)