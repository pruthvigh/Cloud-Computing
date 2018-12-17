from sklearn.cluster import KMeans
from flask import Flask, render_template,request
import os
import pymysql
import csv
# Array processing
import numpy as np
# Data analysis, wrangling and common exploratory operations
import pandas as pd
from pandas import Series, DataFrame
import re
# For visualization. Matplotlib for basic viz and seaborn for more stylish figures
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import random
import matplotlib.cm as cm
app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template("index.html")

@app.route('/add',methods=['POST'])
def loginStudent():
    myConn = pymysql.connect(host='AWS_RDS_MYSQL_HOST_URL', user='USER', passwd='PASSWORD',
                     db='clusterdb',local_infile=True)
    cursor = myConn.cursor()
    name = request.form['name']
    cno = request.form['cno']
    sno = request.form['sno']
    message = "added class successfulyy"
    sqlq = "INSERT INTO enrolled (section_no, course_no, name) VALUES (%s,%s,%s)"
    cursor.execute(sqlq,(sno,cno,name))
    rows = cursor.fetchall()
    myConn.commit()
    sqlq2 = "select * from enrolled"
    cursor.execute(sqlq2)
    rows2 = cursor.fetchall()
    if(cursor.rowcount>30):
       message = "cannot add"
    return render_template('index.html',mess = message)

@app.route('/kmeans', methods=['POST'])
def kmeans():
    df = pd.read_csv('StateVoting.csv', encoding='latin1')

    #col1 = request.form['col1']
    #col2 = request.form['col2']
    
    # df[col1] = pd.to_numeric(df[col1], errors='coerce')
    # df[col2] = pd.to_numeric(df[col2], errors='coerce')
    # df.dropna()
    f1 = df['TotalPop'].values
    f2 = df['PercentVote'].values

    X = np.array(list(zip(f1, f2)))

    plt.rcParams['figure.figsize'] = (16, 9)
    kmeans = KMeans(int(request.form['nclusters']))
    kmeans = kmeans.fit(X)
    
    labels = kmeans.predict(X)
    
    centroids = kmeans.cluster_centers_

    points = kmeans.labels_
    count = []
    #for i in range(len(X)):
        #print("coordinate:", X[i], "label:", labels[i])
    for k in range(0,int(request.form['nclusters'])):
        count.append(len(np.where(points == k)[0]))
    c1 = np.where(points == 1)[0]
    c2 = np.where(points == 2)[0]
    c3 = np.where(points == 0)[0]
    cen = []
    x = np.arange(30)
    ys = [i+x+(i*x)**2 for i in range(30)]
    #colors = ['#2C3E50','#0E6251', '#C0392B', '#F0B27A', '#7D6608','#c92240','#ffccda','#f1ffcc','#1b685b','#965264','#005b96','#eea1b2','#21142b','#180905','#002171']
    colors = cm.rainbow(np.linspace(0, 1, len(ys)))
    plt.figure()
    colour=['blue','green','red','orange','cyan','black','pink','magenta']
    for i, col in zip(range(int(request.form['nclusters'])), colors):
        groups = kmeans.labels_ == i
        centroid = kmeans.cluster_centers_[i]
        cen.append(centroid)
        
        plt.plot(X[groups, 0], X[groups, 1], 'w', markerfacecolor=col, marker='.')
        plt.plot(centroid[0], centroid[1], '*', markerfacecolor=col, markeredgecolor='k', markersize=6)
    plt.title('kmeans')
    print(groups)
    plt.grid(True)
    fno = int(random.randrange(500,1000))
    plt.savefig('static/test'+str(fno)+'.png')
    file = 'static/test'+str(fno)+'.png'
    return render_template('scatter.html',fileno = file)#centroids = centroids,datacount = count)




port = os.getenv('PORT',8080)
if __name__ == '__main__':
    app.run(host = '0.0.0.0',port = port)