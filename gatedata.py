# GateData

# Misc imports
import os
import datetime
import uuid
import string, random

# Flask imports
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, json
from flask import jsonify
from flask import abort, redirect, url_for

# SQL Alchemy imports
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import insert
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import backref
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import column, true


# Gerador de ids para os logs
def uuid_gen():
    return str(uuid.uuid4())


# Base de dados - SQL Alchemy

DATABASE_FILE = "gatedata.sqlite"
db_exists = False
if os.path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False, connect_args={'check_same_thread': False}) #echo = True shows all SQL calls

Base = declarative_base()


# Users table
# - user_id (PK)
# - role
class Users(Base):
    __tablename__  = 'users'
    user_id        = Column(String, primary_key = True)
    role           = Column(String)

# Codes table
class Codes(Base):
    __tablename__ = 'codes'
    code_id   =     Column(String, primary_key = True)
    createdAt = Column(DateTime(timezone=True), default=datetime.datetime.utcnow()) 
    user_id   = Column(String, ForeignKey('users.user_id'))

# Gates table
# - gate_id (PK)
# - location
# - secret
# - number of activations
class Gates(Base):
    __tablename__ = 'gates'
    gate_id  = Column(String, primary_key = True)
    location = Column(String)
    secret   = Column(String)
    n_activations = Column(Integer, default = 0)


Base.metadata.create_all(engine) #Create tables for the data models

Session = sessionmaker(bind=engine)
session = Session()



# INSERTS E UPDATES

def putGate(id, location):
    # Insert or update gate

    q = session.query(Gates).filter(Gates.gate_id == id).first()

    if(q):
        # Update gate
        q.update({Gates.location: location})   
        secret = q.secret
    else:
        # Add gate
        gate = Gates(gate_id = id, location = location)
        session.add(gate)
        secret = gate.secret

    session.commit()
    return secret


##
## USER CODE
##

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
            return jsonify("!!! Code valid !!!")
        else:
            return jsonify("!!! Code not valid !!!")
    else:
        return jsonify("!!! Expired Code !!!")

#Delete Old Code on the Database
def deleteOldCode(user):

    q = session.query(Codes).filter(Codes.user_id == user).delete()
    session.commit()

    return








# Aplicação - Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "Hello"


@app.route('/gates/', methods = ['PUT'])
def registerGate():
    content = request.get_json()
    try:
        # Verify if json content has the correct form
        # ({"gate_id": id, "location": location})
        gate_id = content['gate_id']
        location = content['location']
    except:
        abort()
        #Bad format

    else:
        putGate(gate_id, location)

        # Query for secret 
        result = session.query(Gates.secret).filter(Gates.gate_id == gate_id).all()
    
        # Display secret
        serializable_res = [r._asdict() for r in result]
        return jsonify(serializable_res)

@app.route('/getcode/<user>', methods=['GET'])
def getCode(user):
    if request.method == 'GET':

        #Delete previous code in db
        deleteOldCode(user)
        
        #Create code for gate
        code = code_generator()

        #Inser new code in db
        insertCode(code, user)
        print(code)

        return jsonify(code)
    else:
        abort(400) #BadRequest

@app.route('/usercode/<code>/<user>', methods=['GET'])
def validateUserCode(code, user):
    if request.method == 'GET':
        return isCodeCorrect(code, user)
    else:
        abort(404)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)