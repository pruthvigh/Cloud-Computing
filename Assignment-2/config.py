# edit the URI below to add your RDS password and your AWS URL
# The other elements are the same as used in the tutorial
# format: (user):(password)@(db_identifier).amazonaws.com:3306/(db_name)
import boto3 as boto3
from botocore.client import Config

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://USER:PASSWORD@DB_URL:3306/PhotoApp'

# Uncomment the line below if you want to work with a local DB
#SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

SQLALCHEMY_POOL_RECYCLE = 3600

WTF_CSRF_ENABLED = True
SECRET_KEY = 'SECRET_KEY'


#Connection to S3

#AWS - Secret Key
access_key='ACCESS_KEY'
secret_key= 'SECRET_KEY'
#Bucket Name
my_bucket = 'aws-photo-bucket'

s3Client = boto3.client('s3',aws_access_key_id=access_key,
  aws_secret_access_key=secret_key,
  config=Config(signature_version='s3v4'))

s3resource = boto3.resource('s3')
bucket = s3resource.Bucket(my_bucket)