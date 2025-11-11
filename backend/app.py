from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import pymysql
from datetime import timedelta, datetime
from dotenv import load_dotenv 
import os
from flask_cors import CORS
load_dotenv()
from helpers import *
from tasks import huey, sleepRand,print_pdf
from werkzeug.utils import secure_filename
pymysql.install_as_MySQLdb()

from random import randint
from werkzeug.utils import secure_filename

app = Flask(__name__)


app.config['UPLOAD_FOLDER']=r'D:\PRINTER\uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
db = SQLAlchemy(app)
UPLOAD_FOLDER=r'D:\PRINTER\uploads'

app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.secret_key = "your_secret_key_here"

CORS(
    app,
    supports_credentials=True,   # ✅ allows session cookies
    resources={r"/*": {"origins": "http://127.0.0.1:5500"}}  # ✅ apply to all routes
)
class av:
    Y='Y'
    N='N'
    E='E'

class avm(av):
    Y='YES'
    N='NO'
    E='ERROR'

class BLOCKNAME:
    PG='PG-BLOCK'
    CM='CM-BLOCK'
    IST='1ST-YEAR-BLOCK'
    MB='MB-BLOCK'

#########################################################################################

class PrinterLogin(db.Model):
    ID=db.Column(db.String(20),primary_key=True)
    PASSWORD=db.Column(db.String(20),unique=True)

class PrinterDetail(db.Model):
    PRINTERID=db.Column(db.String(20),primary_key=True)
    ROOMID=db.Column(db.String(10),unique=True)
    BLOCK=db.Column(db.String(20))
    AVAILABLE=db.Column(db.String(1),default=av.Y)



class PendingFile(db.Model):
    __tablename__ = 'PENDINGFILE'
    USERID=db.Column(db.String(20),primary_key=True)
    FILENAME=db.Column(db.Text)
    FILEPATH=db.Column(db.Text)
    OTP = db.Column(db.Integer, nullable=True)

##########################################################################################

##########################################################################################

class User(db.Model):
    __tablename__ = 'user'
    STATICID=db.Column(db.String(50),primary_key=True)
    USERID=db.Column(db.String(20),unique=True, nullable=False)
    EMAIL=db.Column(db.String(40),unique=True, nullable=False)
    PASSWORD=db.Column(db.Text, nullable=False)
    PHONE=db.Column(db.String(20),unique=True, nullable=False)
    USERTYPE=db.Column(db.String(2),nullable=False)

class PendingUser(db.Model):
    __tablename__ = 'pendinguser'
    EMAIL=db.Column(db.String(40),primary_key=True, nullable=False)
    USERID=db.Column(db.String(20),unique=True, nullable=False)
    PASSWORD=db.Column(db.Text, nullable=False)
    PHONE=db.Column(db.String(20),unique=True, nullable=False)
    USERTYPE=db.Column(db.String(2),nullable=False)
    OTP = db.Column(db.String(5),nullable=False)


######################################################################################

class UserHistory(db.Model):
    STATICID=db.Column(db.String(50),primary_key=True)
    TOTALPRINTS=db.Column(db.Integer)
    LASTPRINT=db.Column(db.Date)
    PENDINGFILE=db.Column(db.Text)
    PENDINGFILEOTP = db.Column(db.Integer, nullable=True)





###################ROOT##############
@app.route('/')
def root():
    return """<h1 style='color:red; text-align:center;'>This is root page!
    </h1>"""




####################### PRINTER DASH BOARD FOR SERVER ###################3
@app.route('/printerdash',methods=['GET'])
def prdash():
    block = request.args.get('block')

    if block is not None:
        printers=PrinterDetail.query.filter_by(BLOCK=block.strip().upper()).all()

        pdict={}

        for i in printers:
            pdict[f'{i.PRINTERID}']=[f'{i.ROOMID}',f'{i.BLOCK}',f'{i.AVAILABLE}']

        
        return jsonify(pdict)

    return "None"




################################# DEPRECATED LIST FOR SERVER OF PRINTER #####################
@app.route('/listforserver',methods=['POST','GET'])
def chpravm():
    printers = PrinterDetail.query.all()
    pdict={}

    for i in printers:
        pdict[f'{i.PRINTERID}']=[f'{i.ROOMID}',f'{i.BLOCK}',f'{i.AVAILABLE}']

    return jsonify(pdict)


##############################3 TOGGLE PRINTER YES/NO/ERROR ###################
@app.route('/toggleprinter',methods=['POST'])

def tog():
    pid = request.json.get('printerId')

    printer= PrinterDetail.query.filter_by(PRINTERID=pid.strip().upper()).first()
    print(printer.AVAILABLE)
    printer.AVAILABLE='N' if printer.AVAILABLE == 'Y' else 'Y'
    print(printer.AVAILABLE)
    db.session.commit()

    
    return jsonify(success=True), 200



####################### PRINTER LOGIN  FOR SERVER ##########################

@app.route('/PrinterLogin',methods=['POST'])
def printer():
  printerid=request.json.get('printerid')
  password=request.json.get('password')
  pr = PrinterLogin.query.filter_by(ID=printerid.strip().upper()).first()
  if printerid == pr.ID and pr.PASSWORD==password.strip().lower():
    return jsonify(message=True),200
  else:
    return jsonify(message=False),404



######################## UPLOAD FILE ################################
@app.route('/upload',methods=['POST'])
def giv():
    file = request.files
    userid= request.form.get('userid')
    otp = randint(1000,9999)
    print(file)

    print('OTP FOR :',userid,' IS : ',otp)

    
    if 'file' not in file:
        return jsonify(message="empty request."), 404
    file = file.get('file')
    print(file)
    if not file.filename:
        return jsonify(message="No file selected."), 404
    
    filename = secure_filename(file.filename)

    print(filename)
    
    file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))

    pendingfile = PendingFile(USERID=userid,FILENAME=filename,FILEPATH=os.path.join(app.config['UPLOAD_FOLDER'],filename),OTP=otp)
    db.session.add(pendingfile)
    db.session.commit()
    


    if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'],filename)) :
        print('FILE NOT SAVED')
    return jsonify(message=True),200


@app.route('/printOTP',methods=['POST'])
def printOtp():
    
    if request.json.get('otp')=='1111' or request.json.get('otp')==1111:
        print('invoked printing')
        #printDoc() # type: ignore
        return jsonify(msg=True),200
        
    else :
        return jsonify(msg=False),404



###################### PRINTING THRU REQ ###########################

@app.route('/print',methods=['POST'])
def giv4print():
    file = request.files
    #userid= request.json.get('userid')

    print(file)

    
    if 'file' not in file:
        return jsonify(message="empty request."), 404
    file = file.get('file')
    print(file)
    if not file.filename:
        return jsonify(message="No file selected."), 404
    
    filename = secure_filename(file.filename)

    print(filename)
    
    file.save(os.path.join(app.config['UPLOAD_FOLDER'],file.filename))

    print_pdf(os.path.join(app.config['UPLOAD_FOLDER'],file.filename))


    return jsonify(message='invoked!'),200



@app.route('/triggerprinting',methods=['POST'])
def triggerprinting():
    
    userid = request.json.get('userid')
    eotp = request.json.get('otp')
    print(type(eotp), eotp)
    pendingfile = PendingFile.query.filter_by(USERID=userid).first()
    print(type(pendingfile.OTP), pendingfile.OTP)
    if pendingfile:
        if int(eotp) == pendingfile.OTP:
            filename = pendingfile.FILENAME
            filepath = pendingfile.FILEPATH
            print(filename, 'exists' if os.path.exists(filepath) else 'Doesnt exists')
            if os.path.exists(filepath):
                print_pdf(filepath)
                return jsonify(message='File Found, Otp correct, Added To queue'),200
            
            else:
                print('File Not Found')
                return jsonify(message='File Not Found'),404
        else:
            print('OTP incorrect')
            return jsonify(message='OTP incorrect'),404
    print('File not uploaded')
    return jsonify(message='File not uploaded'),404







@app.route('/rdb')
def rdb():
    userid= request.args.get('userid')
    pp = PendingFile.query.filter_by(USERID=userid).first()
    if pp:
        db.session.delete(pp)
    db.session.commit()
    return 'TRUE DELETED'






############################################## #############################################


@app.route('/register',methods=['POST'])
def reg():
    userid = request.json.get('userid').strip()
    email = request.json.get('email').strip()
    phone = request.json.get('phone').strip()
    password = request.json.get('password').strip()
    usertype = request.json.get('usertype').strip()
    if not all([userid,email,phone,password,usertype]):
        print('All fields are required.')
        return jsonify(message='All fields are required.'),404

    otp = SEND_OTP(email)
    
    puT=PendingUser.query.filter_by(EMAIL=email).first()

    if puT:
        return jsonify(message='User ready for verification!'),200

    pu = PendingUser(
        EMAIL=email,
        USERID=userid,
        PASSWORD=password,
        PHONE=phone,
        USERTYPE=usertype,
        OTP=otp
    )

    try:
        db.session.add(pu)
        db.session.commit()
        f=1
    except Exception as e:
        print(str(e))
        f=0
        return jsonify(message='Some error occured!'),404
    
    if f:
        session['email']=email
        print(session.get('email')) 
        print('user saved in pending user! and session!')
        return jsonify(message='User ready for verification!'),200


@app.route('/verifyForReg', methods=['POST'])
def verReg():
    email = session.get('email')
    eotp = request.json.get('otp', '').strip()

    print(eotp,email)


    if not (eotp and email):
        return jsonify(message='Fields Incomplete!'), 404

    pu = PendingUser.query.filter_by(EMAIL=email).first()
    if not pu:
        return jsonify(message='User not found!'), 404
    print(
        type(eotp),
        eotp,
        type(pu.OTP),
        pu.OTP
    )
    try:
        if pu.OTP == (eotp):
            print('✅ OTP correct for', email)

            
            u = User(
                STATICID=GENERATE_STATIC_ID(pu.USERTYPE, pu.USERID, pu.PHONE),
                USERID=pu.USERID,
                EMAIL=pu.EMAIL,
                PASSWORD=GENERATE_HASH_PASSWORD(pu.PASSWORD),
                PHONE=pu.PHONE,
                USERTYPE=pu.USERTYPE
            )

            db.session.add(u)
            db.session.delete(pu)
            db.session.commit()
            session['FIRSTTIME']=1
            print(' USER VERIFIED & MOVED TO MAIN USER TABLE')
            return jsonify(message='USER VERIFIED!'), 200
        else:
            return jsonify(message='Invalid OTP!'), 404

    except Exception as e:
        print('Error verifying user:', e)
        db.session.rollback()
        return jsonify(message='Some error occurred!'), 500

@app.route('/login',methods=['GET','POST'])
def UserDashboard():
    userid = request.json.get('userid').strip()
    password= request.json.get('password').strip()

    u = User.query.filter_by(USERID=userid).first()
    if not u:
        return jsonify(message='USER NOT FOUND!'),404
    if CHECK_PASSWORD_HASH(password,u.PASSWORD):
        session['STATICID']=u.STATICID
        session.permanent=True
        return jsonify(message='USER LOGGED IN'),200

@app.route('/dashboard')
def dash():
    if session.get('STATICID') is not None:
        if session.get('FIRSTTIME'):
            pu = UserHistory(
                STATICID=session.get('STATICID').strip(),
                TOTALPRINTS=0,
                LASTPRINT=None,
                PENDINGFILE=None
            )
            db.session.add(pu)
            db.session.commit()
            session.pop('FIRSTTIME')
        STATICID=session.get('STATICID')
        pu=UserHistory.query.filter_by(STATICID=STATICID).first()
        u = User.query.filter_by(STATICID=STATICID).first()
        userdict = {
        'user':{
            'userid':u.USERID,
            'email':u.EMAIL,
            'phone':u.PHONE,
            'usertype':u.USERTYPE
        },
        'history':{
            'totalprints':None if not pu.TOTALPRINTS is None else pu.TOTALPRINTS,
            'lastprint':None if not pu.LASTPRINT is None else pu.LASTPRINT,
            'pendingfile':True if pu.PENDINGFILE else False,
        }
        
        }

        return jsonify(userdict),200
    return jsonify(message='USER NOT LOGGED IN'),404


@app.route('/logout',methods=['POST','GET'])
def logout():
    if session.get('STATICID') is not None:
        session['STATICID']=None
        session.pop('STATICID')
        return jsonify(message='DONE!'),200
    return jsonify(message='DONTKNOW'),404

if __name__=='__main__':
    app.run(debug=True,host='0.0.0.0',threaded=True)
