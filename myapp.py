import mimetypes
from flask import *;
import numpy as np
import sqlite3
from PIL import Image
from matplotlib.figure import Figure
from sklearn.feature_extraction import img_to_graph
from werkzeug.utils import secure_filename
import secrets
import os
import base64 
from PIL import Image
from keras.models import load_model
from keras.preprocessing import image
import cv2
import matplotlib.pyplot as plt
import joblib
def getimageuri(p_blob_val):
    return (base64.b64encode(p_blob_val).decode('utf-8').replace('\n',''))

ResNet50_model=load_model("resnet50.h5")

SVM_model=joblib.load("svmcubic.h5")
#SVM_model=joblib.load("liblinearsvm.h5")

class_type = {0:'Covid',  1 : 'Normal'}
con=sqlite3.connect("covid.db")
UPLOAD_FOLDER = 'C:/Users/pc/Desktop/covid project/all_images/tested images'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
print("Database opened succesfully")
#con.execute("drop table patient ")
#con.execute("drop table images ")
#con.execute("drop table Admintable ")
#con.execute("drop table prescription ")


#con.execute("create table Admintable (username varchar(20), passwordKey varchar(20))")
#con.execute("create table Patient (username varchar(20) constraint uni unique, password varchar(20),firstname varchar(20),Lastname varchar(20),Adharnumber NUMBER(12) primary key,Gender varchar(10),Age INTEGER(100),phone integer(10),house_no varchar(20),street varchar(20),city varchar(20),pin_no varchar(6),state varchar(10))")
#con.execute("CREATE TABLE IMAGES(username integer(12),X_ray_photo blob,Xray_Uploaded_date DATE,result varchar(20))")
#con.execute("CREATE TABLE prescription(username integer(12) ,prescription_img blob,uploadeddate DATE)")
            

                    
with sqlite3.connect("covid.db") as con:
    cur=con.cursor()
    username="admin" 
    password="password"
 #   con.execute("INSERT into Admintable (username,passwordKey)values(?,?)",(username,password))

    con.commit()
def render_picture(data):

    render_pic = base64.b64encode(data).decode('ascii') 
    return render_pic

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/',methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route("/adminlogin",methods=['POST'])
def adminlogin():
    flag=0;
    if request.method=='POST':
        user=request.form['username']
        passkey=request.form['passwordkey']
        print(user)
        print(passkey)
        with sqlite3.connect("covid.db") as con:
            cur=con.cursor()
            
            cur.execute("select * from Admintable ;")
            rows=cur.fetchall()
            print(rows)
            for r in rows:
                if (r[0]==user) and (r[1]==passkey):
                    flag=1;
                    
                    return render_template("adminloginpage.html")
                else:
                    
                    continue;
    if flag==0:
        result="Invalid login credentials";
        return render_template('index.html',result=result)
@app.route('/add_patient',methods=['GET','POST'])
def add_patient():
    
    return render_template('Registrationform.html')

@app.route('/upload_image',methods=['GET','POST'])

def upload_image():

    return render_template('upload_xray.html')
@app.route("/savedetails",methods=["post","GET"])
def savedetails():
    msg="msg"
    if request.method=="POST":
        try:
            fname=request.form["firstname"]
            lname=request.form["lastname"]
            adharnumber=request.form["Aadhar"]
            Gender=request.form["Gender"]
            age=request.form["age"]
            phone=request.form["phone"]
            Houseno=request.form["Houseno"]
            street=request.form["street"]
            city=request.form["city"]
            pin_no=request.form["pin_no"]
            state=request.form["state"]
            username=adharnumber
            password=phone
            print(password)
            
            with sqlite3.connect("covid.db") as con:
                cur=con.cursor()
                cur.execute("select * from Patient")
                users=cur.fetchall()
                print('ok')
                flag=1
                for u in users:
                    if (u[0]==username):
                        print(str(u[0]))
                        flag=0;
                        msg="We can not add the patient to the list because user already exist"

                        break;

                if(flag==1):
                    cur.execute("INSERT into Patient (username,password,firstname,Lastname,Adharnumber ,Gender,Age,phone,house_no,street,city,pin_no,state)values(?,?,?,?,?,?,?,?,?,?,?,?,?)",(username,password,fname,lname,adharnumber,Gender,age,phone,Houseno,street,city,pin_no,state))
                    print('ok')
                    con.commit()
                    msg="patient successfully Added"
        except:
            con.rollback()
            
        finally:
            return render_template("adminloginpage.html",result=msg)
@app.route("/saveimages",methods=["post","GET"])
def saveimage():

    msg="msg"
    if request.method=="POST":
        aadharno=request.form["Aadharno"]
        pic = request.files['image']
        print(pic)
        filename = secure_filename(pic.filename)
        print(filename)
        path = os.path.abspath(filename)
        print(path)
        type="hello"
        date=request.form['date']
        pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        try:
            with sqlite3.connect("covid.db") as con:
                cur=con.cursor()
                cur.execute("select * from Patient")
                users=cur.fetchall()
                print('ok')
                flag=1
                for u in users:
                    if (u[0]==aadharno):
                        print(str(u[0]))
                        flag=0;
                        msg="Image added successfully"
                        break;
                if(flag==0):
                    test_data=[]
                
                    p='C:/Users/pc/Desktop/covid project/all_images/tested images/'+filename
                    head_tail = os.path.split(p)
                    fileNo=head_tail[1].split('.') 
                    test_image_o = cv2.imread(head_tail[0]+'/'+fileNo[0]+'.png')
                    test_image = cv2.resize(test_image_o,(65, 65))
                    test_data.append(test_image)
                    test_data = np.array(test_image, dtype="float") / 255.0
                    input_img = np.expand_dims(test_data, axis=0)
                    input_img_feature=ResNet50_model.predict(input_img)
                    input_img_features=input_img_feature.reshape(input_img_feature.shape[0], -1)
                    prediction_SVM = SVM_model.predict(
                        
                    )[0]
                    print(prediction_SVM)
                    if(prediction_SVM==0):
                         type="COVID"
                    elif (prediction_SVM==1):
                        type="Normal"
                    else :
                        type="Viral-Phnemonia"
                    im = open(p,'rb').read()
                    cur.execute("INSERT into IMAGES (username,X_ray_photo,Xray_Uploaded_date,result)values(?,?,?,?)",(aadharno,im,date,type))
                    con.commit()
                else:
                   msg="We can not add the image to the list"
        finally:
            return render_template("adminloginpage.html",result=msg)
            
@app.route("/userlogin",methods=['POST'])

def userlogin():
    flag=0;
    if request.method=='POST':
        user=request.form['username']
        passkey=request.form['password']
        
        print(user)
        print(passkey)
        with sqlite3.connect("covid.db") as con:
            cur=con.cursor()
            cur.execute("select * from Patient where username=? and password=?",(user,passkey,))
            row1=cur.fetchall()
            cur.execute("select * from Images where username=?",(user,))
            row2=cur.fetchall() 
            cur.execute("select * from prescription where username=?",(user,))
            row3=cur.fetchall()
    
            for r in row1:
                if (r[0]==user) and (r[1]==passkey):
                    flag=1;
                    x=r;
                    res_set=[]
                    pre_set=[]
                    for y in row2:
                        ad=y[0]
                        img=getimageuri(y[1])
                        date=y[2]
                        res=y[3]
                        res_set.append([str(y[2]),img,str(y[3])])
                    for x in row3:
                        ad=x[0]
                        img=getimageuri(x[1])
                        date=x[2]
                        pre_set.append([img,str(x[2])])
                    cur.close()
                    
                    return render_template("userpage.html",row1=row1,res_set=res_set,pre_set=pre_set)
                else:
                    
                    continue;
    if flag==0:
        result="Invalid login credentials";
        return render_template('index.html',result=result)
@app.route("/prescription",methods=['GET','POST'])
def prescription():
    if request.method=='POST':
        username=request.form['username']
        pic = request.files['image']
        date=request.form['date']
        Data = pic.read()
        with sqlite3.connect("covid.db") as con:
            cur=con.cursor()
            con.execute("INSERT into prescription(username,prescription_img,uploadeddate)values(?,?,?)",(username,Data,date))
             
            cur.execute("select * from Patient where username=?",(username,))
            row1=cur.fetchall()
            cur.execute("select * from Images where username=?",(username,))
            row2=cur.fetchall() 
            cur.execute("select * from prescription where username=?",(username,))
            row3=cur.fetchall()
            res_set=[]
            pre_set=[]
            for y in row2:
                ad=y[0]
                img=getimageuri(y[1])
                date=y[2]
                res=y[3]
                res_set.append([str(y[2]),img,str(y[3])])
            for x in row3:
                ad=x[0]
                img=getimageuri(x[1])
                date=x[2]
                pre_set.append([img,str(x[2])])
                cur.close()       
    return render_template("userpage.html",row1=row1,res_set=res_set,pre_set=pre_set)

@app.route("/profile",methods=['post'])
def profile():
    return "profile"
if __name__=='__main__':
    app.run(debug=True)