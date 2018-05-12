from flask import Flask, render_template, request, json, redirect, session
from werkzeug import generate_password_hash, check_password_hash
import mysql.connector
import uuid
import os
import time
import Mailer

#create mailer object and go ahead and put in passwords for now . . .

m=Mailer.Mailer()
m.subject='First Try'
m.send_from='notouchmarketingmeasurementapp@gmail.com'
m.attachments=["C:\\Users\\TeamLorenzen\\Documents\\App0\\static\\downloads\\Input Template -- File name will be analysis title.csv"]
m.gmail_password='%like%me'
m.message="Howdy,\nI'm excited to share a very small proof of concept that I've used to learn a bit about cloud computing, web applications, and python.  \n\nIf you have any questions, please reply to this email.\n\nRegards, TL"

#end mailer setup.  

#define flask server
app = Flask(__name__)
app.secret_key = 'I am the very model of a modern major general'
app.config['UPLOAD_FOLDER'] = 'static/Uploads' 

@app.route("/")
def main():
    #return "Yes This App Is Working"
	 return render_template('index.html')

@app.route('/showSignup')
def showSignup():
    return render_template('signup.html')

@app.route('/signUp',methods=['POST','GET'])
def signUp():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
        # validate the received values
        if _name and _email and _password:
            # All Good, let's call MySQL
            conn = mysql.connector.connect(user='root', password='Pi3141592',
                              host='127.0.0.1',
                              database='BucketList',autocommit=True)
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser',(_name,_email,_hashed_password))
            for reg in cursor.stored_results():
               msg=reg.fetchall()
            if not('msg' in locals()):
                #conn.commit()
                m.recipients=[_email]
                m.send_email()
                return render_template('signup.html', message="Your account has been created!",message2="An input template and instructions have been emailed to you.",message3="Please sign in to continue.")
                #return redirect('/showSignin')
                #return json.dumps({'message':'User created successfully !'})
            else:
                 return render_template('error.html',error = 'Username already exists; Sign in or create new account.')
                 #return json.dumps({'error':str(msg[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})
    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()
        
@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')

@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']
        conn = mysql.connector.connect(user='root', password='Pi3141592',
                                  host='127.0.0.1',
                                  database='BucketList')
        cursor = conn.cursor()
        cursor.callproc('sp_validateLogin',(_username,))
        for reg in cursor.stored_results():
            data=reg.fetchall()
        if len(data) > 0:
            if check_password_hash(str(data[0][2]),_password):
                session['user'] = data[0][0]
                session['username']= data[0][1]
                return redirect('/userHome')
            else:
                return render_template('error.html',error='Wrong Email address or Password.')
        else:
            return render_template('error.html',error = 'Email address not found.')
    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close
        conn.close

@app.route('/userHome', methods=['GET', 'POST'])
def userHome():
    if request.method == 'GET':
        if session.get('user'):
            return render_template('userHome.html')
        else:
            return render_template('error.html',error ='Please Sign In')
    if request.method == 'POST':
        struid=session.get('user')
        file = request.files['file']
        f_name = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
        try:
            conn = mysql.connector.connect(user='root', password='Pi3141592',
                                  host='127.0.0.1',
                                  database='BucketList',autocommit=True)
            cursor = conn.cursor()
            cursor.callproc('sp_addinputD',(f_name,struid))
            for rr in cursor.stored_results():
                data=rr.fetchall()
            if not('data' in locals()):
                #success!
                #conn.commit()
                return render_template('userHome.html',message= 'File Uploaded . . .Ingesting Data. . .')#({'message':'User created successfully !'})
            else:
                return render_template('userHome.html',message = 'Username already has a file of that name.')
        except Exception as e:
            return json.dumps({'error':str(e)})
        finally:
            cursor.close() 
            conn.close()
    
@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        #extension = os.path.splitext(file.filename)[1]
        f_name = file.filename#str(uuid.uuid4()) + extension
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
        return render_template('error.html',error='it worked')#json.dumps({'filename':f_name})

if __name__ == "__main__":
    app.run(debug=True)
        
 
    
    
    
    
    
    
    
    
    
    