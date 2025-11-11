
from flask import Flask, abort, make_response, request, send_file, redirect, render_template, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from helpers import *
from flask_cors import CORS
import pymysql
from datetime import timedelta, datetime
from dotenv import load_dotenv 


load_dotenv()


pymysql.install_as_MySQLdb()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
DEVELOPER_LIST =['24B81A62E9','24B81A62J5','24B81A62H9','24B81A62K2','24B81A62G0','24B81A']
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.permanent_session_lifetime = timedelta(days=1)
db = SQLAlchemy(app)

class STATUS():
    ERROR = 'ERROR'
    UNAVAILABLE = 'UNAVAILABLE'
    OVERLOAD = 'OVERLOADED'
    AVAILABLE = 'AVAILABLE'
    WAITLISTED = 'WAITLISTED'
    PRINTING = 'PRINTING'
    PRINTED = 'PRINTED'

class USER_TYPE():
    ADMIN = 'ADMIN'
    STUDENT = 'STUDENT'
    FACULTY = 'FACULTY'
    DEVOLPER = 'DEVELOPER'



class User(db.Model):
    __tablename__ = 'user'
    USER_ID = db.Column(db.String(30), primary_key=True)
    NAME = db.Column(db.String(100), nullable=False)
    PASSWORD = db.Column(db.String(255), nullable=False)
    EMAIL = db.Column(db.String(100), unique=True, nullable=False)
    PHONE_NUMBER = db.Column(db.String(15), unique=True, nullable=False)
    STATIC_ID = db.Column(db.String(512), nullable=True)
    USER_PFP = db.Column(db.Text, nullable=True)
    USER_TYPE = db.Column(db.String(10), nullable=False)
    
    def GET_USER_DETAILS(self):
        return {
            'USER_ID': self.USER_ID,
            'NAME': self.NAME,
            'EMAIL': self.EMAIL,
            'PHONE_NUMBER': self.PHONE_NUMBER,
            'USER_TYPE': self.USER_TYPE,
            'USER_PFP': self.USER_PFP
        }

class PendingUser(db.Model):
    __tablename__ = 'pending_users'
    USER_ID = db.Column(db.String(30), primary_key=True)
    NAME = db.Column(db.String(100), nullable=False)
    PASSWORD = db.Column(db.Text, nullable=False)
    EMAIL = db.Column(db.String(100), unique=True, nullable=False)
    PHONE_NUMBER = db.Column(db.String(15), unique=True, nullable=False)
    USER_TYPE = db.Column(db.String(10), nullable=False)
    IS_VERIFIED = db.Column(db.Boolean, default=False)

    def GET_USER_DETAILS(self):
        return {
            'USER_ID': self.USER_ID,
            'NAME': self.NAME,
            'EMAIL': self.EMAIL,
            'PHONE_NUMBER': self.PHONE_NUMBER,
            'USER_TYPE': self.USER_TYPE,
        }


class Otp(db.Model):
    __tablename__ = 'otp'
    EMAIL = db.Column(db.String(100), primary_key=True)
    OTP = db.Column(db.String(20), nullable=False)
    IS_OTP_CORRECT = db.Column(db.Boolean, default=False)
    STATIC_ID = db.Column(db.String(512), nullable=True)


class Printer(db.Model):
    __tablename__ = 'printer'
    PRINTER_ID = db.Column(db.String(30), primary_key=True)
    STATUS = db.Column(db.String(10), nullable=False, default=STATUS.AVAILABLE)
class File(db.Model):
    __tablename__ = 'file'
    STATIC_ID = db.Column(db.String(512), nullable=False)
    FILE_ID = db.Column(db.String(30), nullable=False, primary_key=True)
    FILENAME = db.Column(db.Text, nullable=False)
    FILETYPE = db.Column(db.String(20), nullable=False)
if not DEVELOPER_LIST:
    raise ValueError("No developer IDs found in DEVELOPER_LIST")
class UserLogs(db.Model):
    __tablename__ = 'user_logs'
    STATIC_ID = db.Column(db.String(512), primary_key=True)
    PRINT_COUNT = db.Column(db.Integer, default=0)
    TOTAL_MONEY_SPENT = db.Column(db.Float, default=0.0)



class Room(db.Model):
    __tablename__ = 'room'
    ROOM_ID = db.Column(db.String(30), primary_key=True)
    PRINTER_ID = db.Column(db.String(30), db.ForeignKey('printer.PRINTER_ID'), nullable=False)
    IS_ROOM_ACTIVE = db.Column(db.Boolean, default=False)

class Queue(db.Model):  
    __tablename__ = 'queue'
    STATIC_ID = db.Column(db.String(512), primary_key=True)
    FILE_ID = db.Column(db.String(30), db.ForeignKey('file.FILE_ID'), nullable=False)
    ROOM_ID = db.Column(db.String(30), db.ForeignKey('room.ROOM_ID'), nullable=False)
    PRINTER_ID = db.Column(db.String(30), db.ForeignKey('printer.PRINTER_ID'), nullable=False)
    STATUS = db.Column(db.String(10), nullable=False, default=STATUS.WAITLISTED)
    CREATED_AT = db.Column(db.DateTime, default=datetime.now())


"""
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://127.0.0.1:6942",
            "http://127.0.0.1:5500",
            "http://localhost:5500"
        ],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})"""


CORS(app, 
     resources={r"/*": {"origins": "*"}},  # For testing, you can use "*"
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])


@app.route('/')
def root():
    user = session.get('user')
    if user:
        ID = user
        if ID:
            return redirect(fr'/404Found/home?ID={ID}')
        else:
            return redirect('/404Found/login')
    return redirect('/404Found/login')

    

@app.route('/404Found/register', methods=['POST'])

def register_user():

    user_id = request.json.get('user_id')

    check_user_exist = User.query.filter_by(USER_ID=user_id).first()

    if check_user_exist:
        print('user already exists')
        return jsonify({'status': 'ERROR','message': 'User ID already exists'}), 400
    
    print('user does not exist')
    
    name = request.json.get('name')
    password = request.json.get('password')
    email = request.json.get('email')
    phone_number = request.json.get('phone_number')
    user_type = request.json.get('user_type')

    userlist = [user_id, name, password, email, phone_number, user_type]



    if not all(userlist):
        print('Missing required fields')
        return jsonify({'status': 'ERROR','message': 'Missing required fields'}), 400
    
    print('all fields are present')
    
    isuserpending = PendingUser.query.filter_by(EMAIL=email).first()
    if isuserpending:
        print('User is already pending')
        
    else:
        pendingUser = PendingUser(USER_ID=user_id,
                              NAME = name, 
                              PASSWORD = password, 
                              EMAIL = email, 
                              PHONE_NUMBER = phone_number, 
                              USER_TYPE = user_type,
                              IS_VERIFIED = False)
        db.session.add(pendingUser)
        db.session.commit()

        print('pending user added')
    userOtp = Otp.query.filter_by(EMAIL=email).first()
    if userOtp:
        userOtp.OTP = SEND_OTP(email)
    else:
        userOtp = Otp(EMAIL=email, OTP=SEND_OTP(email))

    print('otp added')
    db.session.add(userOtp)
    db.session.commit()
    print('commit done')
    return jsonify({'status': 'SUCCESS','message': 'Verification initiated','email':email}), 200


@app.route('/404Found/verify/register/<string:email>', methods=['POST'])
def verify_register(email):
    enteredOtp= request.json.get('otp')
    otp = Otp.query.filter_by(EMAIL=email).first()
    if not otp or not enteredOtp:
        print('One of the otp is missing')
        return jsonify({'status': 'ERROR','message': 'One of the otp is missing'}), 404
    
    print('BOTH OTP ARE PRESENT : ', enteredOtp, otp.OTP)

    if enteredOtp == otp.OTP:
        print('OTP IS CORRECT')
        otp.IS_OTP_CORRECT = True
        user = PendingUser.query.filter_by(EMAIL=email).first()
        user.IS_VERIFIED = True
        createUser = User(
            USER_ID = user.USER_ID,
            NAME = user.NAME,
            PASSWORD = GENERATE_HASH_PASSWORD(user.PASSWORD),
            EMAIL = user.EMAIL,
            PHONE_NUMBER = user.PHONE_NUMBER,
            USER_TYPE = user.USER_TYPE,
            STATIC_ID = GENERATE_STATIC_ID(user.GET_USER_DETAILS())
        )
        db.session.delete(user)
        db.session.add(createUser)
        db.session.delete(otp)
        db.session.commit()
        print('User created successfully')
        return jsonify({'status': 'SUCCESS','message': 'User Verified','email':email}), 200
    
    return jsonify({'status': 'ERROR','message': 'Invalid OTP'}), 401


@app.route('/404Found/login', methods=['POST'])

def login_user():
    if session.get('user'):
        print('User already logged in') #DEBUG LINE
        return redirect(fr'/home?USER_ID={session.get("user")}')
    
    user_id = request.json.get('user_id')
    password = request.json.get('password')

    if not user_id or not password:
        print('Missing required fields') #DEBUG LINE
        return jsonify({'status': 'ERROR','message': 'Missing required fields'}), 400
    
    print('all fields are present') #DEBUG LINE

    user = User.query.filter_by(USER_ID=user_id).first()

    if not user:
        print('User does not exist') #DEBUG LINE
        return jsonify({'status': 'ERROR','message': 'User does not exist'}), 404
    
    print('User exists') #DEBUG LINE

    if not CHECK_PASSWORD_HASH(password, user.PASSWORD):
        print('Invalid password') #DEBUG LINE
        return jsonify({'status': 'ERROR','message': 'Invalid password'}), 401
    print('Password is correct') #DEBUG LINE 

    
    
    session['USER']=user.USER_ID
    print(f"SESSION['USER']={session['USER']}") #DEBUG LINE
    

    session.permanent = True
    return jsonify({'status': 'SUCCESS','message': 'Logged in','email':user.EMAIL}), 200



@app.route('/404Found/home', methods=['GET','POST'])

def home():
    if request.method == 'GET':

        print(session.get('user'))

        if session.get('user'):

            userDetails = User.query.filter_by(USER_ID=request.args.get('userid')).first()
            if not userDetails:
                print('User does not exist')
                return jsonify({'status': 'ERROR','message': 'User does not exist'}), 404
            print('User exists')

            return jsonify({'status': 'SUCCESS','message': 'Home Page','user_details':userDetails.GET_USER_DETAILS()})
        else:
            return redirect('/404Found/login')
        
    return jsonify({'status': 'ERROR','message': 'Invalid request method'}), 405

@app.route('/404Found/logout', methods=['POST','GET'])

def logout_user():
    if not session.get('user'):
        print('User is not logged in')
        return jsonify({'status': 'ERROR','message': 'User is not logged in'}), 401
    
    print('User is logged in')
    session.pop('user', None)
    return jsonify({'status': 'SUCCESS','message': 'Logged out'}), 200



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6942, threaded=True)



