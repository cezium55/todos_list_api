from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

#this is for database file creating of todos.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"

#this is the pipeline connecting python with to the sqlite file
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args = {"check_same_thread":False}
)

#this is session maker where everytime a user makes a request, we open a session to talk to the database
SessionLocal= sessionmaker(autocommit=False, autoflush=False, bind=engine)

#all the database tables will inherit from this base class so sqlalchemy knows about them
base = declarative_base()

class UserDB(base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True, index=True)
    username = Column(String, unique = True, index = True)
    hashed_password= Column(String)

# this is the base class table which will automatically become sql table todos
class TodoDB(base):
    __tablename__ = "todos"
    #defining the tables column and all
    id = Column(Integer, primary_key=True, index = True)
    title = Column(String, index = True)
    completed = Column(Boolean, default=False)
    # links each todo to the user who owns it, so users only ever see their own tasks
    owner_id = Column(Integer, ForeignKey("users.id"), index=True)

#this files looks at the class above and makes the database file in your drive
base.metadata.create_all(bind=engine)
# we are using sqlalchemy ORM with sqlite because you see firstly we can easily migrate this with one line of code change to postgre sql but sqlaclhemy sqlite is used for desktop cli, or small offline applications that stores database along side of python code so the sqlalchemy is a tool which helps in changing the python code into sqlite format and putting protective layer through the use orm right, and above is the basic boiler plate code of how all this works
