#Pruthvi Raj Muthyam
#1001400715
import os
import swiftclient
import keystoneclient
import os
import sys
import pyDes
import hashlib
import swiftclient.client as swiftclient
from flask import Flask
from flask import Flask, render_template, request, make_response, url_for
from random import *
app = Flask(__name__)

auth_url = 'https://identity.open.softlayer.com/v3'
password = 'PASSWORD'
project_id = 'PROJECT_ID'
user_id = 'USER_ID'
region_name = 'dallas'

conn = swiftclient.Connection(
    key = password,
    authurl=auth_url,
    auth_version='3',
    os_options={
        "project_id":project_id,
        "user_id":user_id,
        "region_name":region_name
    })

port = int(os.getenv('PORT',8000))



#Homepage rendering
@app.route('/',methods=['GET','POST'])
def root():
   #files = os.listdir(os.curdir)
   #print(files)
   return render_template("cloud.html")

#PEOPLE_FOLDER = os.path.join('static', 'people_photo')
#app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER

"""
@app.route('/showImage',methods=['GET','POST'])
def show_index():
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'image.jpg')
    return render_template("cloud.html", user_image = full_filename)
"""
#List local files from the directory
@app.route('/listLocalFiles',methods=['GET','POST'])
def listLocalFile():
   files = os.listdir(os.curdir)
   return render_template("cloud.html",files_list=files)
   
#File uploading without checksum
@app.route('/upload_file',methods=['GET','POST'])
def uploadFile():
      if request.method == 'POST':
      container_name = request.form['uploadcontainername']
      f = request.files['file']
      data = f.stream.read()
      size = os.path.getsize(f)
      if(size>10000):
        conn.put_object(big,
                      f.filename,
                      contents= data,#encod(data,'qweasdzx'),
                      content_type='text/plain')
      else:
        conn.put_object(small,
                       f.filename,
                       contents=data,  # encod(data,'qweasdzx'),
                       content_type='text/plain')
      return render_template("cloud.html", msg="File uploaded suceesfully")
"""
#File upload with checksum
@app.route('/upload_file',methods=['GET','POST'])
def uploadFile():
    if request.method == 'POST':
        # fiter=['txt','TXT','text']
        container_name = request.form['uploadcontainername']
        f = request.files['file']
        object_list = []
        hash_list = []

        for obj in conn.get_container(container_name)[1]:
            dataTest = conn.get_container(container_name)[1]
            print( dataTest)
            object_list.append(obj['name'])
            data = conn.get_object(container_name, obj['name'])
            file_contents = data[1]
            #print(file_contents)
            hash = hashlib.md5(file_contents).hexdigest()
            hash_list.append(hash)
            #print(f.filename)
            #print(hash)

        data = f.stream.read()
        md5_returned = hashlib.md5(data).hexdigest()
        print("upload file hash" + md5_returned)
        if f.filename in object_list and md5_returned in hash_list:
            # if filecmp(obj['name'], f.filename):

            conn.put_object(container_name,
                            f.filename,
                            contents=encod(data, 'qweasdzx'),
                            content_type='text/plain')
        elif f.filename in object_list and md5_returned not in hash_list:
            filename = f.filename + " " + str(randint(0, 100))
            conn.put_object(container_name,
                            filename,
                            contents=encod(data, 'qweasdzx'),
                            content_type='text/plain')
        else:

            conn.put_object(container_name,
                            f.filename,
                            contents=encod(data, 'qweasdzx'),
                            content_type='text/plain')

        return render_template("cloud.html")
"""
"""
#Upload  file with backup and current folders
@app.route('/upload_file',methods=['GET','POST'])
def upload():

    if request.method== 'POST':
        # fiter=['txt','TXT','text']
        container_name=request.form['uploadcontainername']
        f=request.files['file']
        object_list=[]
        hash_list=[]
        for obj in conn.get_container(container_name)[1]:
            object_list.append(obj['name'])
            data = conn.get_object(container_name, obj['name'])
            file_contents = data[1]
            #print(file_contents)
            hash= hashlib.md5(file_contents).hexdigest()
            hash_list.append(hash)
            #print(f.filename)
            #print(hash)

        data = f.stream.read()
        md5_returned = hashlib.md5(data).hexdigest()
        #print("upload file hash"+md5_returned)
        if  f.filename in object_list and md5_returned in hash_list:
            # if filecmp(obj['name'], f.filename):
	    container_name="backup-container"
            conn.put_object(container_name,
                            f.filename,
                            contents=encod(data,'qweasdzx'),
                            content_type='text/plain')
        elif f.filename in object_list and md5_returned not in hash_list:
	    container_name="backup-container"
            filename=f.filename+" "+str(randint(0,200))
            conn.put_object(container_name,
                            filename,
                            contents=encod(data,'qweasdzx'),
                            content_type='text/plain')
        else:
	    container_name="current-container"
            conn.put_object(container_name,
                        f.filename,
                        contents=encod(data,'qweasdzx'),
                        content_type='text/plain')


        # enfile=encod(request.files['file'],'aqaqaqaq')



        return render_template("cloud.html",msg="File uploaded suceesfully")
"""        
#Method for encrypting data
def encod(data,key):
    k = pyDes.des(key, pyDes.CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    d = k.encrypt(data)
    return d
#Method for decrypting data    
def decod(data, password):
    password = password.encode('ascii')
    k = pyDes.des(password, pyDes.CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    d = k.decrypt(data)
    return d

#Method for displaying file contents
@app.route('/display_file',methods=['GET','POST'])
def displayFile():
   container_name = request.form['uploadcontainername']
   object_name = request.form['file-name']
   data = conn.get_object(container_name, object_name)
   file_contents = data[1]
   #print(data)
   #with open("Output.txt", "w", newline="") as text_file:
    #   print(file_contents, file=text_file)

   #with open ("Output.txt", "r") as myFile:
   #    con = myFile.readline()
   fileData = open("Output.txt","w")
   fileData.write(file_contents)
   fileData = open("Output.txt","r")
   mess = fileData.readline()
   mess = mess.split("\\r")
   return render_template("cloud.html", outputMessage=mess[0])

#Download file
@app.route('/download_file',methods=['GET','POST'])
def download():
        container_name=request.form['downloadcontainername']
        filenme=request.form['downloadingfile']
        obj = conn.get_object(container_name, filenme)
        file_contents = obj[1]
        actual_file=decod(file_contents,'qweasdzx')

        if request.method == 'POST' :
            response = make_response(actual_file)
            response.headers["Content-Disposition"] = "attachment; filename=%s"%filenme
            print (response)
            return response

#Display files in a container
@app.route('/listfiles',methods=['GET','POST'])
def displayfilesfromcontainer():
    container_name=request.form['conname']
    tag = request.form['append_name']
    object_list=[]
    for data in conn.get_container(container_name)[1]:
        object_list.append(data['name']+tag)
        #object_list.append(data['bytes'])
        #object_list.append(data['last_modified'])
    return render_template("cloud.html",object_list=object_list,container_name= container_name)
    
#Create a new container
@app.route('/createcontiner',methods=['GET','POST'])
def createcontainer():
    container_name =request.form['containername']
    conn.put_container(container_name)
    return render_template("cloud.html",createMes = "Container created successfully")
    
#Delete files from a container
@app.route("/deleteobjects",methods=['GET','POST'])
def deleteobjects():
    container_name=request.form['deleteconater']
    obj_name=request.form['objname']
    conn.delete_object(container_name, obj_name)
    return render_template("cloud.html",fileDel = "File deleted successfully")

#Delete files by a user specified size
@app.route("/delObject1MB",methods=['GET','POST'])
def deleteobjects1MB():
    #print("a")
    sizelength=request.form['fileSize']
    size_int=int(sizelength)
    for container in conn.get_account()[1]:
        for obj in conn.get_container(container['name'])[1]:
            print("b")
            object_size = obj['bytes']
            object_size_int=int(object_size)
            if object_size_int > size_int:
                conn.delete_object(container['name'],obj['name'])
    return render_template("cloud.html",deleteMessage="Files deleted successfully")
    
#Display list of available containers
@app.route('/displaycontainers',methods=["GET",'POST'])
def displaycontainers():
    container_list=[]
    for container in conn.get_account()[1]:
        container_list.append(container['name'])
    return render_template("cloud.html",container_list=container_list)
    
#Delete container    
@app.route('/deletecontainer',methods=["GET",'POST'])
def deletecontainers():
    container_name=request.form['getdeletecontainer']
    conn.delete_container(container_name)
    return render_template("cloud.html",delMsg = "Container deleted successfully")

if __name__ == '__main__':
   app.run(host='127.0.0.1',port=port,debug=True)