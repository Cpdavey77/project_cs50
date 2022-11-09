from flask import Flask, flash, redirect, render_template, request, session, get_flashed_messages
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functions import login_required, check_date, format_date_dmy, time_out_total, current_date_time
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView

from datetime import datetime

#Library for getting my current timezone
from pytz import timezone

#Importing all my tables from my database in base.py
from base import db_session, Users, Leaves, Shifts, Overtimes, Feedbacks, Tasks, Personnels, Managers, Todo

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_TYPE"] = "filesystem"

Session(app)
admin = Admin(app)

#database session
db = db_session()



@app.after_request
def after_request(response):

    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#For creating my own tab in Flask-Admin interfiace
class UserView(BaseView):
    @expose("/", methods = ["GET", "POST"])
    def index(self):
        results = db.query(Users, Feedbacks).join(Feedbacks).all()
        return self.render("admin/feedbacks.html", results=results)

#For adding the tab I created
admin.add_view(ModelView(Users, db))
admin.add_view(UserView(name = "Feedbacks", endpoint = "feedbacks"))


@app.route("/login", methods = ["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:

            flash("Username and Password field is required")
            return redirect("/login")

        else:

            user = db.query(Users).filter_by(username = username).scalar()
            if not user or not check_password_hash(user.hash, password):

                flash("Username/Password does not exist")
                return redirect("/login")

            else:

                session["user_id"] = user.id
                flash("Successful Log-in", "success")
                return redirect("/")

    return render_template("login.html")


@app.route("/", methods = ["GET", "POST"])
@login_required
def index():
        #For Manager side
        if request.method == "POST":

            if request.form["action"] == "add":

                if not request.form.get("title"):

                    flash("Title cannot be empty", "error")
                    return redirect("/")

                elif not request.form.get("description"):

                    flash("Description cannot be empty", "error")
                    return redirect("/")

                todo = Todo(
                    title = request.form.get("title"),
                    user_id = session["user_id"],
                    date_created = current_date_time("date"),
                    description = request.form.get("description")
                )

                #SQL-Alchemy method for inserting to database
                db.add(todo)
                db.commit()

                flash("Task successfully added", "success")

            elif request.form["action"] == "remove":

                db.query(Todo).filter_by(todo_id = request.form.get("todo_id")).delete()
                db.commit()

                flash("Task successully removed", "success")

            return redirect("/")

        tasks = db.query(Tasks).filter_by(user_id = session["user_id"]).all()
        todos = db.query(Todo).filter_by(user_id = session["user_id"]).order_by(Todo.date_created.desc()).all()

        return render_template("index.html", tasks=tasks, todos=todos)


#route for filing leaves of employees
@app.route("/leave_file", methods = ["GET", "POST"])
@login_required
def leave_file():

    if request.method == "POST":

        #function to confirm if dates are valid, i.e. if second date selected...#
        #...is not less than the first date, or if the first date isn't less than...#
        #...the current date.#
        dates = check_date(
            request.form.get("date_start"),
            request.form.get("date_end")
        )

        if not isinstance((dates), dict):

            flash("Invalid date/s", "error")
            return redirect("/leave_file")

        #Date now for my current timezone
        date = datetime.now(timezone("Asia/Singapore"))

        leaves = Leaves(
            user_id = session["user_id"],
            date_filed = date.strftime("%d/%m/%Y - %H:%M"),
            start_date = dates["start"],
            end_date = dates["end"]
        )

        db.add(leaves)
        db.commit()

        flash("Leave successfully filed!", "success")
        return redirect("/leave_file")

    leaves = db.query(Leaves).filter_by(user_id = session["user_id"]).order_by(Leaves.date_filed.desc()).all()
    return render_template("leave_file.html", leaves=leaves)


@app.route("/overtime_file", methods = ["GET", "POST"])
@login_required
def overtime_file():

    if request.method == "POST":
        #get shift id from form
        shift_id = request.form.get("shift_id")

        #get the end shift from shift id selected; if 08:00-16:00, 16:00 will be acquired
        shift = db.query(Shifts).filter_by(shift_id = shift_id).scalar()

        #check wether shift id is valid; a person might change the shift id via elements tab...
        #...in developer tools.
        if not shift:

            flash("Shift Invalid", "error")
            return redirect("/overtime_file")

        elif not request.form.get("ot_date"):

            flash("No date selected", "error")
            return redirect("/overtime_file")

        elif not request.form.get("ot_hours"):

            flash("No number of hours entered", "error")
            return redirect("/overtime_file")

        elif float(request.form.get("ot_hours")) < 1:

            flash("Number of hours cannot be 0 or negative", "error")
            return redirect("/overtime_file")

        #function for calculating what is the actual time_out and total...
        #...number of work-hours ("time out + hours added from overtime")
        time = time_out_total(shift.out, float(request.form.get("ot_hours")))

        date = datetime.now(timezone("Asia/Singapore"))

        overtimes = Overtimes(
            user_id = session["user_id"],
            date_filed = date.strftime("%d/%m/%Y - %H:%M"),
            date = format_date_dmy(request.form.get("ot_date")),
            shift_id = shift_id,
            ot_start = shift.out,   #overtime will start at the end of actual shift
            ot_end = time["out"],   #overtime will end when employee time outs
            total_hours = time["hours"]
        )

        db.add(overtimes)
        db.commit()
        flash("Overtime successfully filed!", "success")
        redirect ("/overtime_file")

    shifts = db.query(Shifts).all()
    overtimes = db.query(Overtimes).filter_by(user_id = session["user_id"]).order_by(Overtimes.date_filed.desc()).all()
    return render_template("overtime_file.html", shifts=shifts, overtimes=overtimes)


@app.route("/contact_admin", methods = ["GET", "POST"])
@login_required
def contact_admin():

    if request.method == "POST":

        if not request.form.get("feedback"):

            flash("Text field cannot be empty", "error")
            return redirect("/contact_admin")

        elif len(request.form.get("feedback")) < 11:

            flash("Text not enough for feedback. Consider adding more", "error")
            return redirect("/contact_admin")

        feedbacks = Feedbacks(
            user_id = session["user_id"],
            feedback = request.form.get("feedback")
        )

        db.add(feedbacks)
        db.commit()

        flash("Feedback sent! Thank you", "success")
        return redirect("/contact_admin")

    return render_template("contact_admin.html")


#Manager webpages

@app.route("/give_tasks", methods = ["GET", "POST"])
@login_required
def give_tasks():

    if request.method == "POST":

        if not request.form.get("title"):

            flash("Title cannot be empty", "error")
            return redirect("/give_tasks")

        elif not request.form.get("deadline"):

            flash("No deadline set", "error")
            return redirect("/give_tasks")

        elif not request.form.get("personnel_id"):

            flash("No personnel selected", "error")
            return redirect("/give_tasks")

        elif not request.form.get("description"):

            flash("Text field cannot be empty", "error")
            return redirect("/give_tasks")

        dates = check_date(
            datetime.now().date().strftime("%Y-%m-%d"),
            request.form.get("deadline")
        )

        if not isinstance((dates), dict):

            flash("Invalid date", "error")
            return redirect("/give_tasks")

        tasks = Tasks(
                user_id = request.form.get("personnel_id"),
                task = request.form.get("title"),
                date_received = dates["start"],
                deadline = dates["end"],
                description = request.form.get("description")
        )

        db.add(tasks)
        db.commit()

        current_employee = db.query(Users).filter_by(id = request.form.get("personnel_id")).scalar()
        flash("Task Successfully given to {}, ".format(current_employee.employee_name), "success")
        return redirect("/give_tasks")

    personnels = db.query(Users).join(Personnels).join(Managers).filter_by(user_id = session["user_id"]).all()
    return render_template("give_tasks.html", personnels = personnels)


@app.route("/filed_leaves", methods = ["GET", "POST"])
@login_required
def filed_leaves():

    if request.method == "POST":

        if request.form["action"] == "approve":

            db.query(Leaves).filter_by(leave_id = request.form.get("leave_id")).update({"status": "Approved"})
            db.commit()
            flash("Approved", "success")
            redirect ("/filed_leaves")

        elif request.form["action"] == "reject":

            db.query(Leaves).filter_by(leave_id = request.form.get("leave_id")).update({"status": "Rejected"})
            db.commit()
            flash("Rejected", "error")
            redirect ("/filed_leaves")

        else:

            flash("Invalid Input", "error")
            redirect ("/filed_leaves")

        redirect ("/filed_leaves")

    results = db.query(Leaves, Users).filter_by(status = "Pending").join(Users).join(Personnels).join(Managers).filter_by(user_id = session["user_id"]).order_by(Leaves.date_filed.desc()).all()
    return render_template("filed_leaves.html", results=results)


@app.route("/filed_overtimes", methods = ["GET", "POST"])
@login_required
def filed_overtimes():

    if request.method == "POST":

        if request.form["action"] == "approve":

            db.query(Overtimes).filter_by(overtime_id = request.form.get("overtime_id")).update({"status": "Approved"})
            db.commit()
            flash("Approved", "success")
            redirect ("/filed_overtimes")

        elif request.form["action"] == "reject":

            db.query(Overtimes).filter_by(overtime_id = request.form.get("overtime_id")).update({"status": "Rejected"})
            db.commit()
            flash("Rejected", "error")
            redirect ("/filed_overtimes")

        else:

            flash("Invalid Input", "error")
            return redirect ("/filed_overtimes")

    results = db.query(Overtimes, Users).filter_by(status = "Pending").join(Users).join(Personnels).join(Managers).filter_by(user_id = session["user_id"]).order_by(Overtimes.date_filed.desc()).all()
    return render_template("filed_overtimes.html", results=results)


@app.route("/logout")
def logout():

    session.clear()
    flash("Logged out")
    return redirect("/login")


@app.context_processor
def homepage_items():

    user = None
    position = None
    user_managers = db.query(Users).filter_by(employee_position = "Manager").all()
    if session.get("user_id"):

        user = db.query(Users).filter_by(id = session["user_id"]).scalar()
        position = db.query(Users).filter_by(id = session["user_id"]).scalar().employee_position

    return dict(user = user, position = position, user_managers=user_managers)


@app.route("/admin/", methods = ["GET", "POST"])
def add_user():

    if request.method == "POST":

        if request.form.get("employee_position"):

            user = Users(
                username = request.form.get("username"),
                hash = generate_password_hash(request.form.get("password")),
                employee_number = request.form.get("employee_number"),
                employee_type = request.form.get("employee_type"),
                employee_position = request.form.get("employee_position"),
                employee_name = request.form.get("employee_name")
            )

            db.add(user)
            db.commit()

            personnel = Personnels(
                user_id = db.query(Users).filter_by(employee_name = request.form.get("employee_name")).scalar().id,
                manager_id = db.query(Managers).filter_by(user_id = request.form.get("manager")).scalar().manager_id
            )

            db.add(personnel)
            db.commit()

        else:

            user = Users(
                username = request.form.get("username"),
                hash = generate_password_hash(request.form.get("password")),
                employee_number = request.form.get("employee_number"),
                employee_type = request.form.get("employee_type"),
                employee_position = "Manager",
                employee_name = request.form.get("employee_name")
            )

            db.add(user)
            db.commit()

            id = db.query(Users).filter_by(username = request.form.get("username")).scalar().id
            manager= Managers(
                user_id = id
            )

            db.add(manager)
            db.commit()

        return redirect("/admin/users")

    else:
        return render_template("/admin/index.html")

@app.route("/admin/feedbacks", methods = ["GET", "POST"])
def feedbacks():

    results = db.query(Users, Feedbacks).join(Feedbacks).all()
    return render_template("/admin/feedbacks.html", results=results)


