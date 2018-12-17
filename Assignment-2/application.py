#import digest as digest
from flask import Flask, render_template, request, session, redirect, url_for, escape, request
from application import db
from application.models import Users, Images
from application.forms import LoginForm
import pymysql
import os, sys
# Elastic Beanstalk initalization
from config import s3Client,bucket

application = Flask(__name__)
application.debug = True
# change this to your own value
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg','txt'])#'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'
application.secret_key = 'SECRET_KEY'
S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format('aws-photo-bucket')

# Global
db = pymysql.connect(host='DB_HOST_URL', user='USER', passwd='PASSWORD',
                     db='PhotoApp')
cur = db.cursor()


@application.route('/')
def index():
    if 'name' in session:
        username = session['name']
        return render_template('homepage.html', user_name=username)

    return render_template('index.html')


@application.route('/userLogin', methods=['GET', 'POST'])
def userLogin():
    if request.method == 'POST':
        userName = request.form['username']
        if not userName.strip():
           return render_template("index.html",error_msg = "Username empty, please enter a username.")
        session['name'] = userName
        query = "SELECT COUNT(*) from users where user_name= %s"
        cur.execute(query,userName)
        result = cur.fetchone()
        rows = result[0]
        if rows>0:
            return render_template('homepage.html', user_name=userName)

        sqlq = "INSERT INTO users(user_name) VALUES (%s)"
        cur.execute(sqlq, userName)
        db.commit()
        return render_template('homepage.html', user_name=userName)

    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@application.route('/uploadPhotos', methods=['GET', 'POST'])
def uploadPhoto():
    #  print(index().name)
    if request.method == 'POST':
        if 'name' in session:
            username = session['name']
        if 'file' not in request.files:
            # flash('No file part')
            return render_template("homepage.html", msg="No file part", user_name=username)
        f = request.files['file']
        if f.filename == '':
            return render_template("homepage.html", msg="No selected file", user_name=username)
        if f and allowed_file(f.filename):

           s3Client.upload_fileobj(
            f,
            'aws-photo-bucket',
            f.filename,
            ExtraArgs={
                "ACL": "public-read",
                "ContentType": f.content_type
            }
        )
        else:
            return render_template("homepage.html", msg="Only images are allowed to upload", user_name=username)
        url = "{}{}".format(S3_LOCATION, f.filename)
        title_form = request.form['title']
        print(url, title_form)
        # timestamp of files:
        for key in s3Client.list_objects(Bucket='aws-photo-bucket')['Contents']:
            #    print key
            filename = key['Key']
            date = key['LastModified']
            # print(date)

        sqlq = "INSERT INTO images(img_url,title,likes,stars,timestamp,user_name) VALUES (%s,%s,%s,%s,%s,%s)"
        print(sqlq)
        cur.execute(sqlq, (url, title_form, 0, 0, date,username))
        db.commit()
    return render_template("homepage.html", msg="Image uploaded suceesfully",user_name=username)


@application.route('/viewphotos', methods=['GET', 'POST'])
def viewPhotos():
    if 'name' in session:
        username = session['name']
    query = "SELECT * from images"
    cur.execute(query)
    data = cur.fetchall()
    return render_template("view.html", data=data,user_name= username)


@application.route('/updateRadio', methods=['GET', 'POST'])
def updateRadio():
    star = request.form['star']
    print(star)
    cur.execute("""
       UPDATE images
       SET stars=%s
       WHERE img_id= '1'""", star)
    db.commit()
    query = "SELECT * from images"
    cur.execute(query)
    data = cur.fetchall()
    return render_template("view.html", data=data)

@application.route('/like', methods=['GET'])
def updateLikes():
    star = request.args['image_id']
    print(star)
    cur.execute("""
       UPDATE images
       SET likes=likes+1
       WHERE img_id= %s""", star)
    db.commit()
    return "Success"


@application.route('/rating', methods=['GET'])
def updateRating():
    img_id = request.args['image_id']
    rating = request.args['rating_form']

    cur.execute("""
       UPDATE images
       SET stars=%s
       WHERE img_id= %s""", (rating, img_id))
    db.commit()
    return "Success"

@application.route('/deleteImage', methods=['GET'])
def deleteImg():
    img_id = request.args['image_id']
    query = "select img_url from images where img_id=%s"
    cur.execute(query,img_id)
    data = cur.fetchall()
    file_name = data[0][0].split('/')
    img_name = file_name[3]
    s3Client.delete_object(
        Bucket='aws-photo-bucket',
        Key=img_name
    )
    query2 = "delete from images where img_id=%s"
    cur.execute(query2,img_id)
    db.commit()
    query3= "SELECT * from images"
    cur.execute(query3)
    data = cur.fetchall()
    return render_template("view.html", data=data,msg="Image deleted successfully")

@application.route('/logout', methods=['GET', 'POST'])
def logout():
    # remove the username from the session if it is there
    session.pop('name', None)
    return redirect(url_for('index'))


port = os.getenv('PORT', '8080')
if __name__ == '__main__':
    application.run(host='0.0.0.0', port=int(port))