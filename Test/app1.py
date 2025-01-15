import os
import sqlite3

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, extract_month_year, extract_dates

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
    user_transaction = db.execute("SELECT * FROM transactions WHERE person_id = ?", user_id)
    transactions = []
    dates = []
    for transaction in user_transaction:
        if transaction["dated"] not in dates:
            dates.append(transaction["dated"])

    options = extract_month_year(dates)
    if len(options) == 0:

        return render_template("index.html", transactions=None, options=None, chosen_option=None, earnings=0, expenses=0)
    chosen_option = options[0]
    chosen_dates = extract_dates(chosen_option)
    counter = 0
    for transaction in user_transaction:
        if transaction["dated"] in chosen_dates:
            transactions.append(
                {
                    "Expense": transaction["flow"],
                    "Date": transaction["dated"],
                    "Payment": transaction["payment"],
                    "Category": transaction["category"],
                    "Amount": transaction["amount"],
                    "Note": transaction["note"],
                }
            )
    for transaction in transactions:
        counter += 1
        transaction["id"] = counter
    if request.method == "POST":
        chosen_option = request.form.get("selected_month")
        print(chosen_option)
        chosen_dates = extract_dates(chosen_option)
        transactions = []
        counter = 0
        for transaction in user_transaction:
            if transaction["dated"] in chosen_dates:
                counter += 1
                transactions.append(
                    {
                        "id": counter,
                        "Expense": transaction["flow"],
                        "Date": transaction["dated"],
                        "Payment": transaction["payment"],
                        "Category": transaction["category"],
                        "Amount": transaction["amount"],
                        "Note": transaction["note"],
                    }
                )
    expenses = 0
    earnings = 0
    for transaction in transactions:
        if transaction["Expense"] == "expense":
            expenses += -(transaction["Amount"])
        else:
            earnings += transaction["Amount"]
    expenses = f"{expenses:.2f}"
    earnings = f"{earnings:.2f}"
    return render_template("index.html", transactions=transactions, options=options, chosen_option=chosen_option, earnings=earnings, expenses=expenses)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        if not request.form.get("flow"):
            return apology("Missing Expenditure Flow", 400)
        elif not request.form.get("date"):
            return apology("Missing Date", 400)
        elif not request.form.get("amount"):
            return apology("Missing Amount", 400)
        elif not request.form.get("method"):
            return apology("Missing Payment Method", 400)
        
        amount = request.form.get("amount")

        if(isint(amount) == False and isfloat(amount) == False):
            return apology("Invalid Amount", 400)
        
        if(isint(amount) == True):
            amount = int(amount)
        else:
            amount = float(amount)

        flow = request.form.get("flow")
        date = request.form.get("date")
        payment = request.form.get("method")
        category = request.form.get("category")
        note = request.form.get("note")
        if flow == "expense":
            amount = -amount
        else:
            amount = amount
        amount = round(amount, 2)
        db.execute("INSERT INTO transactions (person_id, flow, dated, payment, category, amount, note) VALUES (?, ?, ?, ?, ?, ?, ?)", session["user_id"], flow, date, payment, category, amount, note)
        flash("Expenditure Added!", "success")
        return redirect("/")
    else:
        return render_template("add.html")
    
@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    user_id = session["user_id"]
    if request.method == "POST":
        user_transaction = db.execute("SELECT * FROM transactions WHERE person_id = ?", user_id)
        dates = []
        counter = 0
        for date in user_transaction:
            counter += 1
            dates.append(
                {
                    "id": counter,
                    "Meetings": date["meets"],
                    "Tasks": date["tasks"],
                    "Hidden_id": date["id"],
                }
            )

        meets = request.form.get("meets")
        tasks = request.form.get("tasks")
        user_info = [meets, tasks]
        user_category = ["Meetings", "Tasks"]
        user_search = dict(zip(user_category, user_info))
        if user_info == [None, '', '', '', '', '']:
            return render_template("edit.html", dates=dates)
        else:
            user_search_transaction = []
            for date in dates:
                placeholder = []
                print(date)
                for categories, info in user_search.items():
                    print(categories, info)
                    if info == '' or info == None:
                        continue
                    else:
                        print(date[categories], info)
                        if date[categories] == info:
                            print("yes")
                            placeholder.append(date)
                        else:
                            placeholder = []
                            break
                if placeholder != []:
                    user_search_transaction.append(placeholder[0])
            return render_template("edit.html", dates=user_search_transaction)
    else:
        return render_template("edit.html", dates=None)
    
@app.route('/edited/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    user_id = session["user_id"]
            
    if request.method == "POST":
        if not request.form.get("flow"):
            return apology("Missing Expenditure Flow", 400)
        elif not request.form.get("date"):
            return apology("Missing Date", 400)
        elif not request.form.get("amount"):
            return apology("Missing Amount", 400)
        elif not request.form.get("method"):
            return apology("Missing Payment Method", 400)
        
        amount = request.form.get("amount")

        if(isint(amount) == False and isfloat(amount) == False):
            return apology("Invalid Amount", 400)
        
        if(isint(amount) == True):
            amount = int(amount)
        else:
            amount = float(amount)

        flow = request.form.get("flow")
        date = request.form.get("date")
        payment = request.form.get("method")
        category = request.form.get("category")
        note = request.form.get("note")
        if flow == "expense":
            amount = -amount
        else:
            amount = amount
        amount = round(amount, 2)
        db.execute("UPDATE transactions SET flow = ?, dated = ?, payment = ?, category = ?, amount = ?, note = ?, timestamp = CURRENT_TIMESTAMP WHERE id = ?", flow, date, payment, category, amount, note, transaction_id)
        flash("Expenditure Updated!", "success")
        return redirect("/")
    else:
        user_transaction = db.execute("SELECT * FROM transactions WHERE person_id = ?", user_id)
        for transaction in user_transaction:
            if transaction["id"] == transaction_id:
                if transaction["flow"] == "expense":
                    transaction["amount"] = -transaction["amount"]
                unedited_transaction = {
                        "id": 1,
                        "Expense": transaction["flow"],
                        "Date": transaction["dated"],
                        "Payment": transaction["payment"],
                        "Category": transaction["category"],
                        "Amount": transaction["amount"],
                        "Note": transaction["note"],
                        "Ammended": transaction["timestamp"],
                        "Hidden_id": transaction["id"],
                }
                break
        
        return render_template("edited.html", transaction=unedited_transaction)

@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    user_id = session["user_id"]
    if request.method == "POST":
        user_transaction = db.execute("SELECT * FROM transactions WHERE person_id = ?", user_id)
        transactions = []
        counter = 0
        for transaction in user_transaction:
            counter += 1
            amount = transaction["amount"]
            amount = f"{amount:.2f}"
            transactions.append(
                {
                    "id": counter,
                    "Expense": transaction["flow"],
                    "Date": transaction["dated"],
                    "Payment": transaction["payment"],
                    "Category": transaction["category"],
                    "Amount": amount,
                    "Note": transaction["note"],
                    "Ammended": transaction["timestamp"],
                    "Hidden_id": transaction["id"],
                }
            )

        amount = request.form.get("amount")
        flow = request.form.get("flow")
        date = request.form.get("date")
        payment = request.form.get("method")
        category = request.form.get("category")
        note = request.form.get("note")
        user_info = [flow,date,payment,category,amount,note]
        user_category = ["Expense","Date","Payment","Category","Amount", "Note"]
        user_search = dict(zip(user_category, user_info))
        if user_info == [None, '', '', '', '', '']:
            return render_template("delete.html", transactions=transactions)
        else:
            user_search_transaction = []
            for transaction in transactions:
                placeholder = []
                print(transaction)
                for categories, info in user_search.items():
                    print(categories, info)
                    if info == '' or info == None:
                        continue
                    else:
                        print(transaction[categories], info)
                        if transaction[categories] == info:
                            print("yes")
                            placeholder.append(transaction)
                        else:
                            placeholder = []
                            break
                if placeholder != []:
                    user_search_transaction.append(placeholder[0])
            return render_template("delete.html", transactions=user_search_transaction)
    else:
        return render_template("delete.html", transactions=None)
    
@app.route('/deleted/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def delete_transaction(transaction_id):
    user_id = session["user_id"]
    user_transaction = db.execute("SELECT * FROM transactions WHERE person_id = ?", user_id)
    for transaction in user_transaction:
        if transaction["id"] == transaction_id:
            if transaction["flow"] == "expense":
                transaction["amount"] = -transaction["amount"]
            unedited_transaction = {
                    "id": 1,
                    "Expense": transaction["flow"],
                    "Date": transaction["dated"],
                    "Payment": transaction["payment"],
                    "Category": transaction["category"],
                    "Amount": transaction["amount"],
                    "Note": transaction["note"],
                    "Ammended": transaction["timestamp"],
                    "Hidden_id": transaction["id"],
            }
            break
            

    if request.method == "POST":
        db.execute("DELETE FROM transactions WHERE id = ?", transaction_id)
        flash("Expenditure Deleted!", "success")
        return redirect("/")
    else:
        return render_template("deleted.html", transaction=unedited_transaction)

@app.route("/history")
@login_required
def history():
    user_id = session["user_id"]
    user_transaction = db.execute("SELECT * FROM transactions WHERE person_id = ?", user_id)
    transactions = []
    counter = 0
    for transaction in user_transaction:
        counter += 1
        amount = transaction["amount"]
        amount = f"{amount:.2f}"
        transactions.append(
            {
                "id": counter,
                "Expense": transaction["flow"],
                "Date": transaction["dated"],
                "Payment": transaction["payment"],
                "Category": transaction["category"],
                "Amount": amount,
                "Note": transaction["note"],
                "Ammended": transaction["timestamp"],
            }
        )

    return render_template("history.html", transactions=transactions)



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



@app.route("/change", methods=["GET", "POST"])
@login_required
def change():
    user_id = session["user_id"]
    userprofile = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("old_password"):
            return apology("Missing Old Password", 400)

        # Ensure password was submitted
        elif not request.form.get("new_password"):
            return apology("Missing New Password", 400)

        # Ensure password and confirmation is correct
        elif request.form.get("new_password") != request.form.get("confirmation"):
            return apology("New Password don't match", 400)

        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")

        user_password = userprofile[0]["hash"]
        if check_password_hash(user_password, old_password) == False:
            return apology("Old Password does not Match", 400)
        else:
            new_password_hashed = generate_password_hash(new_password)
            db.execute("UPDATE users SET hash = ? WHERE id = ?", new_password_hashed, user_id)

            flash("Password Changed!", "success")
            return redirect("/")
    else:
        return render_template("change.html")


@app.route("/summary", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        if not request.form.get("flow"):
            return apology("Missing Expenditure Flow", 400)
        elif not request.form.get("date"):
            return apology("Missing Date", 400)
        elif not request.form.get("amount"):
            return apology("Missing Amount", 400)
        elif not request.form.get("method"):
            return apology("Missing Payment Method", 400)
        
        amount = request.form.get("amount")

        if(isint(amount) == False and isfloat(amount) == False):
            return apology("Invalid Amount", 400)
        
        if(isint(amount) == True):
            amount = int(amount)
        else:
            amount = float(amount)

        flow = request.form.get("flow")
        date = request.form.get("date")
        payment = request.form.get("method")
        category = request.form.get("category")
        note = request.form.get("note")
        if flow == "expense":
            amount = -amount
        else:
            amount = amount
        amount = round(amount, 2)
        db.execute("INSERT INTO transactions (person_id, flow, dated, payment, category, amount, note) VALUES (?, ?, ?, ?, ?, ?, ?)", session["user_id"], flow, date, payment, category, amount, note)
        flash("Expenditure Added!", "success")
        return redirect("/")
    else:
        return render_template("add.html")