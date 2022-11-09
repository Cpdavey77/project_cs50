# Employee Portal
#### Video Demo:  <https://www.youtube.com/watch?v=v1X54UFIELM>
#### Description:
My project is a simple Employee Portal where employees can file their Leaves and Overtimes and a Manager account can approve or reject them.

I'm going to begin on the tools I used in creating this web application.

## Tools
The tools are used are: **Python**(*Programming Language*), **Flask**(*Web Application Framework*), **Flask-Admin**(*Flask extension for admin interface*), and **SQLAlchemy**(*Python SQL toolkit and Object Relational Mapper*)
I used Flask-Admin so that I can manage and add users for the employee portal. Then I used SQLAlchemy for managing, and acquiring data from a database I created called **employee.db**. Instead of creating my own classes, I first created manually with a desktop app called **DB Browser**, and then mapped the created database to Python using SQLAlchemy. I used SQLAlchemy instead of Flask-SQLAlchemy since using the former can let me create existing classes in a seperate file which I named **base.py**. Then I imported the classes to my **app.py**.

## Static Folder
The first folder in my project is that Static Folder. Here, I have a subfolder called **js** where my javascript files are. I compiled most of my javascript files in my **textfields_manager.js** file. In this .js file, all of my front end validation functions are here. I studied and used **Jquery** to create my functions. in my **table_status.js**, this .js file is for changing the color of the status of the filed leaves or filed overtimes in either green, red, or orange, depending if they're pending, approved, or rejected. All of my html styles are stored inside the **styles.css** file.

## Templates Folder
Inside this folder are where all of my templates are stored. Notice there is an admin subfolder. I learned that, while using Flask-admin, if I want to edit or create my own column in the Flask-admin interface, I can create templates that extends the original layout created by Flask-admin using the jinja code **{% extends "admin/master.html" %}**
The next special thing I added is that tabs seen by the user is different depending if the user is a **manager** or a **normal employee**. This can be seen in the **layout.html** file and in **index.html** file.

## app.py
This is where the backend of my project exists. I imported multiple libraries to aid in my project like **flask_admin**(for admin page), **datetime**(for time-related functions), and **pytz**(for acquiring time zone). I also imported the classes of my database from the **base.py** file. The **db_session** is for creating a session when app.py is ran.

### UserView
This class is for creating a new column in the Flask-admin interface. I passed the feedbacks table from the database to the **admin/feedbacks.html** template.

### ModelView
This is for mapping a class from the database to a seperate column in Flask-admin. I like how Flask-admin easens the management of a database by giving the user **CRUD** capabilities to a database.

### login
This is a route to the login page. It has validation where it will flash an alert and redirect the user back to the login page if no credentials are inputted, or if the inputted credentials do not exist.

### index
This is a route for the homepage of my web application. If there is no user in session, the decorator **login_required** redirects the user back to the login page. The POST method of the index page exists in the Manager account where he can create a To-Do list, and in my code, it will insert it into or remove from the table **Todo** inside the database. I created back-end validations if no user input is in the POST request. For the GET request, I passed queries for both the manager and normal employee account for the creation of their table in the index page.

### leave file
This is a route where employees can file their leave. I created a function called **check_date()** that can be seen in the **functions.py** file. It checks wether the two dates inputted by the user is valid or not. It is invalid when: the second date if earlier than the first one, or if the first date isnt less than the current date. I also used the function **isinstance** since my check_date() function either returns a dictionary of the two modified dates, or a error string. If it returns a string, it flash an alert and redirect the user to the same page and not submitting his/her inputs in the program. If the inputs are valid, the function will then insert the data into the **Leaves** table inside the database.

### overtime file
This is a route where employees can file their overtimes. I created multiple validations to check for user input and flash alerts if they did not pass the checks. Next I created another function called **time_out_total** to add the number of overtime_hours inputted by the user to his/her actual time-out in the company. it returns a dictionary that has **out** and **hours** as keys to insert into the database. Next is I used the library **datetime** and **pytz** to acquire the current date and time based on my current timezone. After these processes, I then inserted data into the **Overtimes** table in the database.

### contact admin
This is a route where users can give feedback or suggestions to the admin managing their accounts. Then those feedbacks are inserted in the **Feedbacks** table in the database.

### give tasks
The first route for the manager is this. This route is where a manager can give tasks to employees assigned to him/her. I created validations for user input and used the check_date() function again to check wether the input for **deadline** is more or less than the current date. After these validations, it will then insert the data in the **Tasks** table in the database.

### filed leaves
This is a route where a manager can approve or reject filed leaves by his/her employees. It has two processes: when the manager approves, and when the manager rejects the filed leave. After clicking a button, either approve or reject, it will update the status of the filed leave in the database to either "Approved" or "Rejected".

### filed overtimes
This is a route where a manager can approve or reject filed overtimes by his/her employees. The functionality of this route is almost the same to the filed leaves route.

### logout
This is a route where clears the current session and redirects the user to the login page when a user clicks the Log Out button.

### homepage items
This function is wrapped in a context processor. From what I have read online, context processors lets you create global variables to pass them automatically to all templates in your templates folder. Instead of passing them repeatedly in multiple templates, you just have to create one context processor and they will automatically avaiable to call in your templates using Jinja code.
Here, I passed 3 global variables. **user** and **position** are for the user profile while the **user_managers** is for the flask-admin page.

### add user
This route I created for the Flask-admin index page lets an admin add a user to the database. It does multiple inserts in multiple tables for relating the different tables inside my database.

### feedbacks
This is a route where an admin can check for feedbacks sent by his/her users.

## base.py
This is the file where I initialized SQLAlchemy to map my database to Python. I used the automap method instead of reflect. The **sessionmaker** function lets me create a database session to let me type in queries to acquire/edit data from/to the database.

## employee.db
This is the database file I used for my whole project. The tables that exists are :
**Users**(User data)
**Leaves**(Leaves filed by employees)
**Shifts**(Shift ids for softcoding them in the input option in the overtime_file.html)
**Overtimes**(Overtimes filed by employees)
**Feedbacks**(Feedbacks submitted by users)
**Tasks**(Tasks given by managers to an employee)
**Personnels**(Relates employees to their respective managers)
**Managers**(Creates a unique id for Managers)
**Todo**(Stores the list of todos created by the managers)

## functions.py
This file is where most of the functions I created to be used in app.py. The function **format_date_dmy** lets me modify the default format of date from <input type="date">
to my own liking: date-month-year. The current_date_time() function returns the current date or time depending on the argument. It takes 2 kinds of strings: "date" or "time".