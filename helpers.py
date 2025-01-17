from flask import redirect, render_template, request, session
from functools import wraps
from datetime import datetime, timedelta


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


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

def extract_month_year(dates):
    formatted_months = []
    dates = sorted(dates, key=lambda x: datetime.strptime(x, '%Y-%m-%d'))
    for date_str in dates:
        # Convert the date string to a datetime object
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        # Format the date as "Month Year" (e.g., "June 2024")
        formatted_month = date_obj.strftime('%B %Y')
        if formatted_month not in formatted_months:
            formatted_months.append(formatted_month)

    return formatted_months

def extract_dates(month):
    # Convert the month string to a datetime object
    month_obj = datetime.strptime(month, '%B %Y')
    # Get the first and last day of the month
    first_day = month_obj.replace(day=1)
    last_day = month_obj.replace(day=1, month=month_obj.month % 12 + 1) - timedelta(days=1)
    # Get all the dates in the month
    dates = []
    current_day = first_day
    while current_day <= last_day:
        dates.append(current_day.strftime('%Y-%m-%d'))
        current_day += timedelta(days=1)

    return dates