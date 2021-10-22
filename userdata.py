# UserData

from gatedata import Codes

# Misc imports
import datetime
import string, random
import os

# Flask imports
from flask import Flask, request

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

# Base de dados - SQL Alchemy

DATABASE_FILE = "gatedata.sqlite"
db_exists = False
if os.path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False, connect_args={'check_same_thread': False}) #echo = True shows all SQL calls

Base = declarative_base()

Base.metadata.create_all(engine) #Create tables for the data models

Session = sessionmaker(bind=engine)
session = Session()


# Aplicação - Flask
app = Flask(__name__)


def code_generator(size=6, chars=string.ascii_uppercase + string.digits):
   return ''.join(random.choice(chars) for _ in range(size))

#Insert data in Codes Table in DB
def insertCode(code, user):

    q = session.query(Codes).filter(Codes.user_id == user).first()
    print(q) #None

    if(q):
        # Update Code
        q = session.query(Codes).filter(Codes.user_id == user).update({Codes.user_id : user})
    else:
        #Add code for new user
        codedb = Codes(code_id = code, user_id = user)
        session.add(codedb)

    session.commit()

    return code

#Verify if code is expired (1 min)
def isCodeExpired(code, user):

    q = session.query(Codes).filter(Codes.user_id == user).first()
    time = datetime.datetime.utcnow()
    expired = q.createdAt + datetime.timedelta(minutes=1)

    if(time < expired):
        return False
    else:
        return True

#Verify if code introduced matches with the one in the database
def isCodeCorrect(code, user):

    q = session.query(Codes).filter(Codes.user_id == user).first()

    if (isCodeExpired(code, user) == False):
        if (code == q.code_id):
            return "!!! Code valid !!!"
        else:
            return "!!! Code not valid !!!"
    else:
        return "!!! Expired Code !!!"

#Delete Old Code on the Database
def deleteOldCode(user):

    q = session.query(Codes).filter(Codes.user_id == user).delete()
    session.commit()

    return


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)