from flask import Flask, render_template, request, json, redirect, session
from werkzeug import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'I am the very model of a modern major general'
    
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
                conn.commit()
                return redirect('/showSignin')
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
                return redirect('/userHome')
            else:
                return render_template('error.html','Wrong Email address or Password.')
        else:
            return render_template('error.html',error = 'Email address not found.')
    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close
        conn.close

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html',error ='Please Sign In')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
        
 
    
    
    
    
    
    
    
    
    
    