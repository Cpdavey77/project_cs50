from functools import wraps
from flask import redirect, render_template, request, session
from datetime import datetime, timedelta
from pytz import timezone

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

#to convert date formatting to D-M-Y
def format_date_dmy(date):
    string_date = datetime.strptime(date, "%Y-%m-%d").date()
    return string_date.strftime("%d/%m/%Y")

#process two dates to determine if 2nd date is less than the first date
def check_date(date1, date2):

    if not date1 or not date2:
        return "error0"
    try:
        date_1 = datetime.strptime(date1, "%Y-%m-%d").date()
        date_2 = datetime.strptime(date2, "%Y-%m-%d").date()
    except ValueError:
        return "invalid date"
    else:
        now = datetime.now().date()

        #check if date is before the current date
        if date_1 < now or date_2 < now:
            return "error1"
        #check if the second date is less than the first date
        elif date_2 < date_1:
            return "error2"
        else:
            dates = {
                "start": date_1.strftime("%d/%m/%Y"),
                "end": date_2.strftime("%d/%m/%Y")
            }
            return dates

#accepts two strings: either "date" or "time"
def current_date_time(type):
    date_time = datetime.now(timezone('Asia/Singapore'))
    if type == "date":
        date = date_time.strftime("%d/%m/%Y")
        return date
    elif type == "time":
        time = date_time.strftime("%H:%M:%S")
        return time
    else:
        return None

def time_out_total(time_out, added_hours):#
    try:
        t_out = datetime.strptime(time_out, "%H:%M")
    except ValueError:
        return "error"
    else:
        time_add = t_out + timedelta(hours=added_hours)

        time = {
            "out": time_add.strftime("%H:%M"),
            "hours": 8 + float(added_hours)
        }
        return time

