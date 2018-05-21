from flask import Flask, render_template, request, json, redirect, session, url_for
from werkzeug import generate_password_hash, check_password_hash
import mysql.connector
import uuid
import os
import time
import Mailer
import pandas as pd
import numpy as np
import MKTransforms
import plotly2json
#%tbimport math

#create mailer object and go ahead and put in passwords for now . . .

m=Mailer.Mailer()
m.subject='How to use the No Touch Marketing Measurement webapp'
m.send_from='notouchmarketingmeasurementapp@gmail.com'
m.attachments=["C:\\Users\\TeamLorenzen\\Documents\\App0\\static\\downloads\\Input Template -- File name will be analysis title.csv"]
m.gmail_password='%like%me'
m.message="Thanks for signing up!\nI'm excited to share a small prototype of marketing analytics 'as a service' I built to integrate my understandiing of cloud computing, web applications, and a variety of open source tools. \n\nIf you have any questions, please reply to this email.\n\nRegards, TL"

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
                #querystring2="update tbl_user set user_lastlogin = NOW() where user_id="+str(data[0][0])+";"
                #cursor.execute(querystring2)
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
            try:
                conn = mysql.connector.connect(user='root', password='Pi3141592',
                                      host='127.0.0.1',
                                      database='BucketList')
                cursor = conn.cursor()
                querystring="Select data_filename from tbl_datafiles where user_id="+str(session.get('user'))+"&& data_resultsname IS NOT NULL;"
                cursor.execute(querystring)
                results=cursor.fetchall()
                #results is list of tuples;
                #trim off part before _ and extension
                resNames=[]
                resFiles=[]
                for r in results:
                    startchar=int(r[0].find('_')+1)
                    endchar=int(r[0].find('.'))
                    resNames.append(r[0][startchar:endchar])
                    resFiles.append(r[0][0:len(r[0])-4]+'results.json')
                    #resFiles.append(r[1])
                betterResults=zip(resFiles,resNames)
                return render_template('userHome.html', results=betterResults)
            except Exception as e:
                return json.dumps({'error':str(e)})
        else:
            return render_template('error.html',error ='Please Sign In')
        
    if request.method == 'POST':
        struid=session.get('user')
        file = request.files['file']
        f_name = str(struid)+"_"+file.filename
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
                triggerModel=1
                rawdf=pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
                #reate model data with user provied transforms
                depMeans,depV,IDnames, groups, transforms, knownSigns, origDep,datadf=MKTransforms.MKTransforms(rawdf)
                #run models and select best (altough first pass just runs one model, no sign constraint)
                intcoef, X1, Y1 =MKTransforms.runModels(depV,IDnames,groups, knownSigns, origDep,datadf)
                #create decomps
                origSpaceDecomp,modSpaceDecomp, =MKTransforms.decomp0(X1,Y1,origDep,intcoef,depV,depMeans,transforms,rawdf,IDnames)
                #group decomps
                groupedDecomp=MKTransforms.makeGroupedDecomp(origSpaceDecomp,groups,depV)
                #compute elasticites
                elasts=MKTransforms.calcElast(intcoef,X1,IDnames,groups, transforms)
                #make plotly dashboard
                figAll=MKTransforms.createDash(groupedDecomp,IDnames,rawdf,groups,elasts)
                #dump to json
                f_nameNoExt=os.path.splitext(f_name)[0]
                jsonname=os.path.join(app.config['UPLOAD_FOLDER'], f_nameNoExt+'results.json')
                plotly2json.plotlyfig2json(figAll, jsonname)
                #tag it in database
                cursor.callproc('sp_addresults',(jsonname,struid))
                #need to learn how to get upload message on page while using the redirect to trigger the results
                #return render_template('userHome.html',message= 'File Uploaded . . .Ingesting Data. . .')
                return redirect(url_for('userHome',message='File Ingested Sucessfully'))
            else:
                return render_template('userHome.html',message = 'Username already has a file of that name.')
        except Exception as e:
            return json.dumps({'error':str(e)})
        finally:
            #close mysql connectino
            cursor.close() 
            conn.close()                

def skipthisstuff():
     if triggerModel==1:
                #import data
                rawdf=pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
                #reate model data with user provied transforms
                depMeans,depV,IDnames, groups, transforms, knownSigns, origDep,datadf=MkTransforms(rawdf)
                #run models and select best (altough first pass just runs one model, no sign constraint)
                intcoef, X1, Y1 =runModels(depV,IDnames,groups, knownSigns, origDep,datadf)
                #create decomps
                origSpaceDecomp,modSpaceDecomp, =decomp0(X1,Y1,origDep,intcoef,depV,depMeans)
                #group decomps
                groupedDecomp=makeGroupedDecomp(origSpaceDecomp,groups)
                #compute elasticites
                elasts=calcElast(intcoef,X1,IDnames,groups, transforms)
                #compute current vs past changed by time id decomps
                YoY,aggGroupedDecomp=createDash(groupedDecomp,IDnames,rawdf)
                #make plotly dashboard
                figAll=createDash(groupedDecomp,IDnames,rawdf)
                #dump to json
                
                plotlyfig2json(figAll, os.path.join(app.config['UPLOAD_FOLDER'], f_nameNoExt+'results.json'))
                #put name into database (with date)
                #cursor.callproc('sp_addresults',(f_name,struid,f_name+'results.json'))

@app.route('/logout')
def logout():
        struid=session.get('user')
        try:
            conn = mysql.connector.connect(user='root', password='Pi3141592',
                                              host='127.0.0.1',
                                              database='BucketList',autocommit=True)
            cursor = conn.cursor()
            querystring2='update tbl_user set user_lastlogin = NOW() where user_id='+str(struid)+';'
            cursor.execute(querystring2)
            cursor.close()
            conn.close()
            session.pop('user',None)
            return redirect('/')
        except Exception as e:
            return json.dumps({'error':str(e)})
            
    
@app.route('/makeDash/<resultsfile>', methods=['GET','POST'])
def makeDash(resultsfile):
    try:
        #have to chop off first / in path for some reason
        thisJson=os.path.join(app.config['UPLOAD_FOLDER'], resultsfile)
        #thisJson='static/Uploads/'+resultsfile
        premade=plotly2json.plotlyfromjson(thisJson)
        return render_template('dashboard.html',premade=premade)
    except Exception as e:
        return json.dumps({'error':str(e)})


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        #extension = os.path.splitext(file.filename)[1]
        f_name = file.filename#str(uuid.uuid4()) + extension
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
        return render_template('error.html',error='it worked')#json.dumps({'filename':f_name})

if __name__ == "__main__":
    app.run()
        
 
    
    
    
    
    
    
    
    
    
    