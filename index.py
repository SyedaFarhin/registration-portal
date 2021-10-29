from flask import Flask 
from flask import render_template
from flask import request
from flask import session
from flask import redirect, url_for
from flask_pymongo import PyMongo
# pip install Flask-Mail   FOR SENDING MAIL
from flask_mail import Mail, Message
import math, random
import datetime

app = Flask(__name__)
app.secret_key = "neha"  # For Create Session

#FOR SENDING EMAIL FOLLOWING CONFIGUARATION REQUIRED
e_mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'syedafarhin18@gmail.com' #'yourId@gmail.com'
app.config['MAIL_PASSWORD'] = 'maihoonna'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True



#mongodb_client = PyMongo(app, uri="mongodb+srv://syeda:syeda18@newcluster.doivb.mongodb.net/projectDatabase?retryWrites=true&w=majority")
mongodb_client = PyMongo(app, uri="mongodb://localhost:27017/GMIT_Flask_Mongo")
db = mongodb_client.db

@app.route('/')
def indexpage():
    return render_template('index.html')

@app.route('/aboutus')
def aboutuspage():
    return render_template('about.html')


@app.route('/contactus',methods=['GET', 'POST'])
def contactuspage():
    
    if request.method == 'GET':
        
        return render_template('contact.html')
    else:
        db.messagecollection.insert_one(
        {'name':request.form['name'],
        'useremail':request.form['useremail'],
        'subject':request.form['subject'],
        'message':request.form['message'],
        })
        
        return render_template('contact.html',msg="MESSAGE SENT")

@app.route('/contactmentor',methods=['GET', 'POST'])
def contactmentorpage():
    
    if request.method == 'GET':
       
        return render_template('contactmentor.html')
    else:
        db.studentmessage.insert_one(
        {'name':request.form['name'],
        'subject':request.form['subject'],
        'message':request.form['message'],
        'rollno':request.form['rollno'],
        })
        
        return render_template('contactmentor.html',msg="MESSAGE SENT")


@app.route('/branches')
def branchespage():
    return render_template('branches.html')


@app.route('/events')
def eventspage():
    return render_template('events.html')

@app.route('/gradestudent', methods=['GET', 'POST'])
def gradepage():
    if request.method == 'GET':
        return render_template('gradestudent.html')
    else:
        db.gradecollection.insert_one(
        {'srollno' : request.form['srollno'],
         'sem' : request.form['sem'],
         'amarks': request.form['amarks'],
         'imarks':request.form['imarks'],
         'remarks' : request.form['remarks'],
         'sgpa' : request.form['sgpa'],
         'cskill' : request.form['cskill'],
         'mname' : session['name'],
         'memail' : session['email'],
         })
        return render_template('gradestudent.html',msg='SUBMITTED SUCCESFULY')




@app.route('/studentreg', methods=['GET', 'POST'])
def studentregpage():
    if request.method == 'GET':
        return render_template('student.html')
    else:
        db.usercollection.insert_one(
        {'name' : request.form['sname'],
         'password' : request.form['spassword'],
         'gender': request.form['sgender'],
         'department':request.form['sdep'],
         'email' : request.form['semail'],
         'rollno' : request.form['srollno'],
         'phnno' : request.form['sphnno'],
         'address' : request.form['saddress'],
         'batch' : request.form['sbatch'],
         'mname' : request.form['name'],
         'memail' : request.form['email'],
         'datetime': datetime.datetime.now()
         })
        email_msg = Message('SUBJECT LINE', sender = 'syedafarhin18@gmail.com', recipients = [request.form['semail']])
        email_msg.body = "WELCOME...REGISTRATION SUCCESS.."
        e_mail.send(email_msg)
        return render_template('student.html', msg='REGISTRATION SUCCESFUL')
        
def OTPgenerator() :
	digits_in_otp = "0123456789"
	OTP = ""

# for a 4 digit OTP we are using 4 in range
	for i in range(4) : 
		OTP += digits_in_otp[math.floor(random.random() * 10)] 

	return OTP 


@app.route('/studentlogin', methods=["GET", "POST"])
def studentloginpage(): 
    if request.method == 'GET': 
        return render_template('studentlogin.html')
    else:
        user=db.usercollection.find(
        {
        'email': request.form['semail'],
        'password': request.form['spassword'],
        })
        print(user)
        if user:
            email_msg = Message('SUBJECT LINE - OTP', sender = 'syedafarhin18@gmail.com', recipients = [user['email']])
            gen_otp = OTPgenerator()
            print(gen_otp)
            email_msg.body = "YOUR OTP " + gen_otp
            e_mail.send(email_msg)
            return render_template('studentotp.html',oriotp = gen_otp,email=user['email'],password=user['password']) 
        else:
            return render_template('studentlogin.html', errormsg = "INVALID UID OR PASSWORD")

@app.route('/studentotpcheck', methods=["POST"])  
def studentOTPCheck(): 
    if request.form['sotp'] == request.form['originalotp']:
        session['email']= request.form['semail']
        session['name']= request.form['sname']
        session['type']= 'Student'
        return redirect(url_for('studenthome'))
    else:
        return render_template('studentotp.html',errormsg = "INVALID OTP",oriotp = request.form['originalotp'],email=request.form['semail'],name = request.form['sname'])  

 
@app.route('/mentorlogin', methods=["GET", "POST"])
def mentorloginpage(): 
    
    if request.method == 'GET': 
        return render_template('mentorlogin.html')
    
    else:
        
        user=db.mentorcollection.find_one(
        {
        'email' : request.form['email'],
        
        
         })
        print(user)
        if user:
            session['email']= user['email']
            session['name']= user['name']
            session['type']= 'Mentor'
            return render_template('aftermentorlogin.html',tname=user['name'])
        else:
            return render_template('mentorlogin.html',errormsg="INVALID")  
            



@app.route('/adminlogin', methods=['GET','POST'])  
def adminloginpage(): 
    if request.method == 'GET':
        return render_template('admin.html')
    else:      
        adminuid = request.form['auid']
        adminpassword = request.form['apassword']

        if(adminuid == 'admin' and adminpassword == 'admin'):
            session['type']= 'ADMIN'
            return render_template('afteradminlogin.html',utype='ADMIN')
        else:
            return render_template('admin.html', msg = 'INVALID UID OR PASS')

@app.route('/viewstudent', methods=['GET', 'POST'])
def viewstudent():
    if request.method == 'GET':
        return render_template('inviewstudent.html')
    else:
        userobj = db.usercollection.find_one({'rollno':request.form['srollno']})
        print(userobj)
        if userobj:
            return render_template('inviewstudent.html', userdata = userobj,show_results=1)
        else:
            return render_template('inviewstudent.html', errormsg = "INVALID EMAIL ID")
            
            
@app.route('/viewstudentprofile')  
def viewStudentProfile(): 
    srollno = session['rollno']      
    studentobj = db.usercollection.find_one({'rollno': srollno})
    print(studentobj)
    return render_template('viewstudentprofile.html', uobj = studentobj)
    
@app.route('/viewStudentByMentor')  
def viewstudentpage(): 
    u1 = db.usercollection.find({})
    return render_template('viewstudent.html', userdata = u1)

@app.route('/viewmentor')  
def viewmentor(): 
    u2 = db.mentorcollection.find({})
    return render_template('viewmentor.html', userdata = u2)
        
    


@app.route('/viewgrade')  
def viewgrade(): 
    userobj = db.gradecollection.find({"srollno":session['rollno']})
    print(userobj)
    return render_template('viewgrade.html', userdata = userobj)

@app.route('/viewallgrades')  
def viewallgrades(): 
    userobj = db.gradecollection.find({})
    print(userobj)
    return render_template('viewallgrades.html', userdata = userobj)
    
@app.route('/message')  
def viewmessage(): 
    usermessage = db.messagecollection.find({})
    return render_template('viewmessage.html', query = usermessage)
    
@app.route('/viewstudentmsg')  
def viewstudentmessage(): 
    usermessage = db.studentmessage.find({})
    return render_template('studentmessage.html', query = usermessage)
    


@app.route('/updatstudentprofile', methods=["GET", "POST"])  
def updateStudentProfile():
    if request.method == 'GET':
        srollno = session['rollno']      
        studentobj = db.usercollection.find_one({'rollno': srollno})
        return render_template('updatestudentprofile.html',uobj = studentobj)
    else:
        db.usercollection.update_one( {'rollno': session['rollno'] },
        { "$set": { 
                    'password': request.form['pass'],
                    'address': request.form['address'] 
                  } 
        })
        return redirect(url_for('viewStudentProfile'))

@app.route('/afteradminlogin')  
def adminafterlogin(): 
    return render_template('afteradminlogin.html')

@app.route('/search', methods=['GET','POST'])  
def searchstudent(): 
    if request.method == 'GET':
        return render_template('searchstudent.html')
    else:      
        userobj = db.usercollection.find_one(
        {'rollno': request.form['srollno']
        })
        print(userobj)
        
        if userobj:
            #print(userobj['username'])
            return render_template('searchstudent.html', userdata = userobj,show_results=1)
       
        else:
             userobj = db.usercollection.find_one(
             {'department': request.form['srollno']
             })
             if userobj:
                 return render_template('searchstudent.html', userdata = userobj,show_results=1)
             else:
                 return render_template('searchstudent.html', errormsg = "INVALID Phone No")

@app.route('/searchmentor', methods=['GET','POST'])  
def searchmentor(): 
    if request.method == 'GET':
        return render_template('searchmentor.html')
    else:      
        userobj = db.mentorcollection.find_one(
        {'email': request.form['email']
        })
        print(userobj)
        
        if userobj:
            #print(userobj['username'])
            return render_template('searchmentor.html', userdata = userobj,show_results=1)
       
        else:
             userobj = db.mentorcollection.find_one(
             {'department': request.form['email']
             })
             if userobj:
                 return render_template('searchmentor.html', userdata = userobj,show_results=1)
             else:
                 return render_template('searchmentor.html', errormsg = "INVALID")    





    
            
             
@app.route('/studenthome')
def studenthome():
    return render_template('afterstudentlogin.html')
    
@app.route('/aftermentorlogin')
def teacherhome():
    return render_template('aftermentorlogin.html')
                 
        





        
        
@app.route('/admentor', methods=['GET', 'POST'])
def addmentor():
    if request.method == 'GET':
        return render_template('addmentor.html')
    else:
        db.mentorcollection.insert_one(
        {'name' : request.form['name'],
        'department' : request.form['dep'],
        'email' : request.form['email'],
        'datetime': datetime.datetime.now()
         
         
        })
        return render_template('addmentor.html')
        

        
@app.route('/assignmentor', methods=["GET", "POST"])  
def assign_mentor():
    if request.method == 'GET':
        return render_template('assignmentor.html')
    else: 
        u1=db.usercollection.find_one({'rollno': request.form['rollno'] })
        u2=db.mentorcollection.find_one({'email': request.form['email']})
        print(u2)
        if u1:
            if u2:
                db.usercollection.update_one( {'rollno': request.form['rollno'] },
                { "$set": { 'mname': request.form['name'],
                    'memail': request.form['email'],
                } 
                })
            else:
                return render_template('assignmentor.html',msg='INVALID MENTOR EMAIL')
        else:
            return render_template('assignmentor.html',msg='INVALID STUDENT ROLL')
       

@app.route('/delete', methods=['GET','POST'])  
def deleteUser(): 
    if request.method == 'GET':
        return render_template('delete.html')
    else:
        u1=db.usercollection.find_one({'rollno': request.form['rollno'] })
        print(u1)
        u2=db.mentorcolection.find_one({'email': request.form['email']}) 
        if u1:
            responsefrommongodb = db.usercollection.find_one_and_delete({'rollno': request.form['rollno']})
            print(responsefrommongodb)
            if responsefrommongodb is not None:                
                return render_template('delete.html', msg = "SUCCESSFULLY DETELED")
        responsefrommongodb2 = db.mentorcollection.find_one_and_delete({'email': request.form['email']})
        return render_template('delete.html', msg = "SUCCESSFULLY DETELED")        
    return render_template('delete.html', msg = "INVALID EMAIL ID")

@app.route('/delete1', methods=['POST'])  
def deleteUser1():
    print(request.form['rollno']) 
    responsefrommongodb = db.usercollection.find_one_and_delete({'rollno': request.form['rollno']})
    print(responsefrommongodb)
    return redirect(url_for('viewall'))





@app.route('/logout')  
def logout():  
    if 'type' in session:  
        session.pop('type',None)  
        return render_template('index.html');     
    else:  
        return '<p>user already logged out</p>' 
        
if __name__ == '__main__':
    app.run(debug=True)  
