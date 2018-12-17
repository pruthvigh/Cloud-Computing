
from flask import Flask,render_template,request,jsonify
import pymysql
import time
import hashlib
import json
import csv
import random
from datetime import datetime
import sys,os
from dateutil import parser

#
headers=[]
myConn = pymysql.connect(host='AWS_RDS_HOST_URL', user='USER', passwd='PASSWORD',
                     db='PhotoApp',local_infile=True)

app = Flask(__name__)
memcach = memcache.Client(['AWS_MEMCACHE_ENDPOINT'], debug=0)

@app.route('/')
def hello_world():
     return render_template('index.html')

# creating table using the csv and importing the data
@app.route('/createtable',methods=['POST'])
def createtable():
    
    cursor = myConn.cursor()
    file_name = 'C:/Users/Administrator/Desktop/Starbucks.csv'
    droptbl = "DROP TABLE IF EXISTS PhotoApp.starbucks;"
    cursor.execute(droptbl)
    with open(file_name, 'rt', encoding= 'Latin-1') as csvfile:
        reader = csv.reader(csvfile,quotechar='`')
        headers = next(reader)
    
    start_time = time.time()
    
    sqlcreate="create table if not exists starbucks("
    for i in range(0, len(headers)):
         sqlcreate +=  headers[i] + " varchar(100),"
    sqlcreate += "Idautonum int AUTO_INCREMENT PRIMARY KEY)"
    cursor.execute(sqlcreate)
    
    uploadqry="""LOAD DATA LOCAL INFILE 'C:/Users/Administrator/Desktop/Starbucks.csv'
          INTO TABLE starbucks FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\r' IGNORE 1 ROWS;"""
    cursor.execute(uploadqry)
    myConn.commit()
    
    end_time = time.time()
    query2 = "Select count(*) from starbucks"
    cursor.execute(query2)
    data = cursor.fetchall()
    time_diff = end_time - start_time
    cursor.close()
    return render_template('index.html',crtimerds=time_diff,success = "Data inserted into database",nr = data[0])

# Fetching the earthquake data where magnitude between 3 and 6
@app.route('/fetch',methods=['POST'])
def fetch():
    res=[]
    lat = request.form['sat1']
    lon = request.form['sat2']
    
    city=request.form['city']
    
    cursor = myConn.cursor()
    st = time.time()
    
    query1 = "SELECT INSTNM FROM education  where SAT_AVG between %s AND %s and CITY = %s limit 3"
    
    
    cursor.execute(query1,(lat,lon,city))
    et = time.time()
    
    data = cursor.fetchall()
    cursor.close()
    print (data)
    count=0
    for row in data:
        count=count+1
        res.append("Institute Name:"+row[0])
    return render_template('index.html', res=res,count=count,tt = et-st)

@app.route('/random',methods=['POST'])
def randomGen():
    ran=[]
    count = request.form['count']
    
    cursor = myConn.cursor()
    st = time.time()
    for i in range(1, int(count)+1):
        rand_number = random.randrange(900,1100)
        rno = int(rand_number)
        print (rno)
        sqlq = "SELECT INSTNM FROM education WHERE SAT_AVG = %s"
        print (sqlq)
        cursor.execute(sqlq, rno)
    et = time.time()
    time_diff = et - st
    data = cursor.fetchall()
    count=0
    for row in data:
        count=count+1
        # res.append("Latitude:"+ row[1]+ "  ; Longitude:"+row[2])
        ran.append("Institute name: "+row[0])
    return render_template('index.html', resur=ran,countrr=count,ttr = et-st)

@app.route('/random2',methods=['POST'])
def randomGen2():
    ran=[]
    count = request.form['count']
    
    cursor = myConn.cursor()
    st = time.time()
    for i in range(1, int(count)+1):
        rand1 = random.randrange(35,40)
        rand2 = random.randrange(42,47)
        lat1 = int(rand1)
        lat2 = int(rand2)
        print (lat1)
        print (lat2)
        sqlq = "SELECT Name FROM starbucks where CountryCode = %s and Latitude between %s and %s"
        print (sqlq)
        cursor.execute(sqlq, ('US',lat1,lat2) )
    et = time.time()
    time_diff = et - st
    data = cursor.fetchall()
    count=0
    for row in data:
        count=count+1
        # res.append("Latitude:"+ row[1]+ "  ; Longitude:"+row[2])
        ran.append('Name: '+row[0])
    return render_template('index.html', resu2=ran,countr2=count,tt2 = et-st)

@app.route('/memc',methods=['POST'])
def memcac():

    lat = request.form['lat1']
    lon = request.form['lon1']
    cursor = myConn.cursor()
    newlat=request.form['lat2']
    newlon =request.form['lon2']
    code = request.form['ccode']
    result=[]
    results = []
    mc = "yes"
    st = time.time()
    result = memcach.get(lat+lon+newlat+newlon+code)
    if not result:
        sqlselect = "SELECT City FROM starbucks where Latitude between %s AND %s and Longitude between %s and %s and CountryCode = %s"
        cursor.execute(sqlselect,(lat,newlat,lon,newlon,code))
        result = cursor.fetchall()
        mc = "no"
        print(result)
        
        memcach.set(lat+lon+newlat+newlon+code, result)
    et = time.time()
    time_diff = et -st
    cursor.close()
    count = 0;
    for row in result:
        count = count + 1
        # results.append(row)
        
        results.append(str(row[0]))
    
    return render_template('index.html', resu=results, countr = count,foundm=mc,tt = time_diff)

@app.route('/updaterows', methods=['POST'])
def selectDQuery():
    cursor = myConn.cursor()
    sqlq = "UPDATE starbucks SET Name= %s where Latitude between %s and %s and CountryCode = %s"
    cursor.execute(sqlq,(request.form['name'],request.form['lat_1'],request.form['lat_2'],request.form['ccode']))
    #cursor.execute('SELECT GivenName, City, State FROM testdb.table_1 where city like \'%' + request.form.get('city') +  ;')
    result = cursor.fetchall()
    myConn.commit()
    print(result)
    return render_template('index.html', msg="Rows updated")

@app.route('/updatename', methods=['GET'])
def updatename():
    cursor = myConn.cursor()
    newid = request.args['sid']
    newname = request.args['nname']
    print(newid)
    sqlup = "UPDATE starbucks set name = %s where id =  %s"
    cursor.execute(sqlup, (newname,newid))
    myConn.commit()
    return "Success" #render_template('index.html',nameup = "Name updated successfully")
    
@app.route('/updaterowssingle', methods=['POST'])
def selectDbQuery():
    cursor = myConn.cursor()
    sqlq = "select ID,Name from starbucks where Latitude between %s and %s and CountryCode = %s LIMIT 5"
    cursor.execute(sqlq,(request.form['lat_1'],request.form['lat_2'],request.form['ccode']))
    #cursor.execute('SELECT GivenName, City, State FROM testdb.table_1 where city like \'%' + request.form.get('city') +  ;')
    result = cursor.fetchall()
    print(result)

    return render_template('index.html', data = result)


@app.route('/innerjoin',methods=['POST'])
def join():
    joinresult=[]

    cursor = myConn.cursor()
    st = time.time()
    
    query1 = "SELECT s.name, u.state FROM starbucks as s,uszipcodes as u where s.city = u.city and s.CountryCode = 'US' LIMIT 10"
    
    cursor.execute(query1)
    et = time.time()
    
    data = cursor.fetchall()
    count=0
    for row in data:
        count=count+1
        joinresult.append("Place:"+row[0]+ "State:"+row[1])
    return render_template('index.html', resujoin=joinresult,joinrows=count,timejoin = et-st)

@app.route('/delcache',methods=['POST'])
def dcache():
    memcach.flush_all()
    return render_template('index.html', cd = "Cache deleted successfully")

@app.route('/createindex',methods=['POST'])
def crindex():
    tab = request.form['table']
    col = request.form['column']
    cursor = myConn.cursor()
    st = time.time()
    query = "CREATE INDEX index2 ON "+str(tab)+"("+str(col)+")"
    cursor.execute(query)
    myConn.commit()
    et = time.time()
    return render_template('index.html', inmes = "Index created successfully")



port = os.getenv('PORT', '8080')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(port))


