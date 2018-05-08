from flask import Flask, render_template, request, json
from werkzeug import generate_password_hash, check_password_hash
import mysql.connector

app0 = Flask(__name__)
    
@app0.route("/")
def main():
    #return "Yes This App Is Working"
	 return render_template('index.html')

@app0.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app0.route('/signUp',methods=['POST','GET'])
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
                return json.dumps({'message':'User created successfully !'})
            else:
                return json.dumps({'error':str(msg[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})
    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()


if __name__ == "__main__":
    app0.run()
        
 
    
    
    
    
    
    
    
    
    
    