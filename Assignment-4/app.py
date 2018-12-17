#PRUTHVI RAJ MUTHYAM
#1001400715
from flask import Flask,render_template,request,jsonify,make_response
import pymysql
import csv
import random
import sys,os
from dateutil import parser
import csv
   

#
headers=[]

app = Flask(__name__)

@app.route('/')
def hello_world():
     return render_template('index.html')

# creating table using the csv and importing the data
@app.route('/createtable',methods=['POST'])
def createtable():
    
    myConn = pymysql.connect(host='AWS_RDS_URL', user='USER', passwd='PASSWORD',
                     db='cloud',local_infile=True)
    cursor = myConn.cursor()
    file_name = 'C:/Users/Administrator/Desktop/StateVotingClean.csv'
    dropTable = "DROP TABLE IF EXISTS cloud.statevoting;"
    cursor.execute(dropTable)
    with open(file_name, 'rt', encoding= 'Latin-1') as csvfile:
        reader = csv.reader(csvfile,quotechar='`')
        headers = next(reader)
    
    start_time = time.time()
    
    sqlcreate="create table if not exists statevoting("
    for i in range(0, len(headers)):
         sqlcreate +=  headers[i] + " varchar(100),"
    sqlcreate += "Idautonum int AUTO_INCREMENT PRIMARY KEY)"
    cursor.execute(sqlcreate)
    
    uploadqry="""LOAD DATA LOCAL INFILE 'C:/Users/Administrator/Desktop/StateVotingClean.csv'
          INTO TABLE statevoting FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;"""
    cursor.execute(uploadqry)
    myConn.commit()
    
    end_time = time.time()
    time_diff = end_time - start_time
    cursor.close()
    return render_template('index.html',timeTaken=time_diff,success = "Data inserted into database")


@app.route('/bar2',methods=['POST'])
def getbar():
   
   myConn = pymysql.connect(host='AWS_RDS_URL', user='USER', passwd='PASSWORD',
                     db='cloud',local_infile=True)
   lat1 = request.form['lat1']
   lat2 = request.form['lat2']
   long1 = request.form['lon1']
   long2 = request.form['lon2']
   code = request.form['code']
   cursor = myConn.cursor()
   
   sqlq = ("select INSTNM,SAT_AVG from education where CITY IN (select city from starbucks where CountryCode = %s AND Latitude >="+str(lat1)+" AND Latitude <="+str(lat2)+
                        " AND (Longitude >="+str(long1)+" AND Longitude <="+str(long2)+")) limit 10")
   
   res = cursor.execute(sqlq,code)
   
   data = cursor.fetchall()
   print(data)
   fno = int(random.randrange(500,1000))
   myFile = open('./static/data'+str(fno)+'.csv', 'w',newline='')
   with myFile:
       cw = csv.writer(myFile)
       print("in file write")
       cw.writerow([i[0] for i in cursor.description])
       cw.writerows(data)
   cursor.close()
   myConn.close()
   return render_template('bar2.html',fileno = str(fno))

@app.route('/vote',methods=['POST'])
def getvote():
   
   myConn = pymysql.connect(host='AWS_RDS_URL', user='USER', passwd='PASSWORD',
                     db='cloud',local_infile=True)
   pop1 = request.form['pop1']
   pop2 = request.form['pop2']
   
   cursor = myConn.cursor()
   
   sqlq = "SELECT StateName,VotePop FROM statevoting where Voted between %s and %s limit 5"
   
   res = cursor.execute(sqlq, (pop1,pop2))
   
   data = cursor.fetchall()
   print(data)
   fno = int(random.randrange(500,1000))
   myFile = open('./static/data'+str(fno)+'.csv', 'w',newline='')
   with myFile:
       cw = csv.writer(myFile)
       print("in file write")
       cw.writerow([i[0] for i in cursor.description])
       cw.writerows(data)
   cursor.close()
   myConn.close()
   return render_template('piechart2.html',fileno = str(fno))

port = os.getenv('PORT', '8080')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(port))


