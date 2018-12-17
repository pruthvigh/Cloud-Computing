from flask import Flask, render_template, request, session, redirect, url_for, escape, request
import pymysql
import os, sys,io,csv,glob,time
from google.cloud import storage

application = Flask(__name__)
application.debug = True
application.secret_key = 'testkey'
db = pymysql.connect(host='GCP_DB_HOST_URL', user='USER', passwd='PASSWORD',
                    db='food',local_infile=True)
cur = db.cursor()

calDel = ""
@application.route('/')
def index():
    
    # file_name = 'C:/Users/pruthviraaz41/Desktop/TestApp/descriptions.csv'
    # droptbl = "DROP TABLE IF EXISTS food.images;"
    # cur.execute(droptbl)
    # with open(file_name, 'rt', encoding= 'Latin-1') as csvfile:
    #     reader = csv.reader(csvfile,quotechar='`')
    #     headers = next(reader)
    
    # start_time = time.time()
    
    # sqlcreate="create table if not exists images("
    # for i in range(0, len(headers)):
    #      sqlcreate +=  headers[i] + " varchar(100),"
    # sqlcreate += "Idautonum int AUTO_INCREMENT PRIMARY KEY)"
    # cur.execute(sqlcreate)
    
    # uploadqry="""LOAD DATA LOCAL INFILE 'C:/Users/pruthviraaz41/Desktop/TestApp/descriptions.csv'
    #       INTO TABLE images FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\r' IGNORE 1 ROWS;"""
    # cur.execute(uploadqry)
    # db.commit()
    
    
    return render_template('index.html')


@application.route('/uploadData', methods=['GET', 'POST'])
def uploadData():
    #  print(index().name)

    ingredients = []
    calories = [];
    genre = []
    file_list = glob.glob('data/*.csv')
    for file in file_list:
      fname = file.split('\\')[1]

      fpath = 'data/{}'.format(fname)
      print(fpath)
      with open(fpath, 'r') as f:
        reader = csv.reader(f)
        lines = list(reader)
      url = 'https://storage.googleapis.com/clouda8/{}.jpg'.format(fname.split('.')[0])
      name = f.name.split('.')[0]
      img_name = '{}.jpg'.format(name)
      upload_blob('clouda8',img_name,'{}.jpg'.format(fname.split('.')[0]))
      
      
      ingredients = lines[1]
      calories = lines[0]
      genre = lines[2][0]
      tot_cal = 0
      for cal in calories:
          if cal is "":
              cal = 0
          tot_cal = tot_cal + int(cal)
      dictionary = dict(zip(ingredients, calories))
      list_key_value = [[k, v] for k, v in dictionary.items()]
      cur.execute("insert into items(name,type,img_url,calorie) values(%s,%s,%s,%s)", (fname.split('.')[0],genre,url,tot_cal))
      db.commit()
      item_id = cur.lastrowid
      for var in list_key_value:
          var.insert(1, item_id)

      with db.cursor() as cursor:
        cursor.executemany("insert into ingredients(name,item_id,calories) values (%s,%s,%s)",list_key_value)
        db.commit()
    message = "Success"
    return render_template("index.html",msg = message)


@application.route('/calorieRange', methods=['GET', 'POST'])
def calories():
    st = time.time()
    creator = request.form['creator']
    des = '%{}%'.format(creator)
    st1 = time.time()
    et1 = time.time()
    query = "select * from images where Description like %s"
    cur.execute(query,des)
    
    data = cur.fetchall()
    et = time.time()
    gaptime = et1-st1
    timediff = et-st
    return render_template('view.html',data = data,time1 = gaptime,time2 = timediff)

@application.route('/ingDisplay', methods=['GET', 'POST'])
def ing():
    st = time.time()
    ing = request.form['ing']
    st1 = time.time()
    query = "select * from items,ingredients as ing where items.id=ing.item_id and ing.name = %s"
    cur.execute(query,ing)
    et1 = time.time()
    data = cur.fetchall()
    et = time.time()
    gaptime = et1-st1
    timediff = et-st
    return render_template('view.html',data = data,time1 = gaptime,time2 = timediff)

@application.route('/rename', methods=['GET', 'POST'])
def rename():
    st = time.time()
    desc = '%{}%'.format(request.form['desc'])
    rename = request.form['rename']
    st1 = time.time()
    query = "update images set FileName = %s where Description like %s"
    cur.execute(query,(rename,desc))
    db.commit()
    et1 = time.time()
    data = cur.fetchall()
    
    query3 = "select * from images"
    cur.execute(query3)
    data = cur.fetchall()
    et = time.time()
    gaptime = et1-st1
    timediff = et-st
    return render_template('view.html',data = data,time1 = gaptime,time2 = timediff)

@application.route('/delShow', methods=['GET', 'POST'])
def delShow():
    st = time.time()
    global calDel
    cal = request.form['creator']
    calDel = cal
    
    st1 = time.time()
    query = "select * from images where Creator = %s"
    cur.execute(query,cal)
    et1 = time.time()
    data = cur.fetchall()
    et = time.time()
   
    return render_template('delete.html',data = data,cal = calDel)

@application.route('/delImages', methods=['GET', 'POST'])
def delImages():
    st = time.time()
    
    cal = returnCalDel()
    cal2 = cal
    print(cal)
    st1 = time.time()
    query = "delete from images where Creator = %s"
    cur.execute(query,cal2)
    db.commit()
    query = "select FileName from images"
    cur.execute(query)

    et1 = time.time()
    data = cur.fetchall()
    et = time.time()
    dm = "images deleted "
    return render_template('delete.html',dm = data)

@application.route('/ingName', methods=['GET', 'POST'])
def ingName():
    st = time.time()
    ingold = request.form['ing-old']
    ingnew = request.form['ing-new']
    st1 = time.time()
    query = "update ingredients set name = %s where name = %s"
    cur.execute(query,(ingnew,ingold))
    db.commit()
    et1 = time.time()
    data = cur.fetchall()
    et = time.time()
    mess = "updated successfully"

    return render_template('index.html',mess = mess)

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))

def returnCalDel():
	return calDel

port = os.getenv('PORT',8080)
if __name__ == '__main__':
   application.run(host = '0.0.0.0',port = port)