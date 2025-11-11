
from random import randint as rd
from flask import Flask, request, response,redirect,url_for, session, jsonify
app=Flask(__name__)
@app.route("/register",methods=["POST"])
def register():
    userid=request.form.get("userid") 
    email=request.form.get("email") 
    phone=request.form.get("phone")
    password=request.form.get("password")
    ValidList=[userid,email,phone,password]
    if all(ValidList):
        return jsonify(variablename="all fields are required")
    
    otp=rd(1111,9999) 
    return otp
        


@app.route("/login",methods=["POST"])
def login():
    userid=request.form.get("userid")
    password=request.form.get("password")
    class user():
        staticid='usha'
        password='123'
    u1=user()
    if password==u1.password:
        session['user']=u1.staticid
        return True
    else:
        return "password doesn't match"
        
@app.route("/logout")
def logout():
    if "staticid" in session: 
        session.pop("staticid",None)
        return "user logge d out " 
    else:
      return "user is not logged out"