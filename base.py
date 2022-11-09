from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

Base = automap_base()
engine = create_engine("sqlite:///employee.db", connect_args={"check_same_thread": False})

Base.prepare(autoload_with=engine)

#Map the tables from my database
Users = Base.classes.users
Leaves = Base.classes.leaves
Shifts = Base.classes.shifts
Overtimes = Base.classes.overtimes
Feedbacks = Base.classes.feedbacks
Tasks = Base.classes.tasks
Personnels = Base.classes.personnels
Managers = Base.classes.managers
Todo = Base.classes.todo

db_session = sessionmaker(bind=engine)

db = db_session()

