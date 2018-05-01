import boto3
import os 


BUCKETEER_AWS_ACCESS_KEY_ID=  os.getenv('BUCKETEER_AWS_ACCESS_KEY_ID','')
BUCKETEER_AWS_REGION= os.getenv('BUCKETEER_AWS_REGION','')
BUCKETEER_AWS_SECRET_ACCESS_KEY= os.getenv("BUCKETEER_AWS_SECRET_ACCESS_KEY", "")
BUCKETEER_BUCKET_NAME= os.getenv("BUCKETEER_BUCKET_NAME", "") 



print(BUCKETEER_AWS_ACCESS_KEY_ID)
print(BUCKETEER_AWS_REGION)
print(BUCKETEER_AWS_SECRET_ACCESS_KEY)
print(BUCKETEER_BUCKET_NAME)


boto3.set_stream_logger(name='botocore')

s3 = boto3.client('s3',aws_access_key_id=BUCKETEER_AWS_ACCESS_KEY_ID,aws_secret_access_key=BUCKETEER_AWS_SECRET_ACCESS_KEY)
filename = 'image003.jpg'
bucket_name = BUCKETEER_BUCKET_NAME
s3.upload_file(filename, bucket_name, 'public/' + filename)
url ="https://"+BUCKETEER_BUCKET_NAME + '.s3.' + BUCKETEER_AWS_REGION + '.amazonaws.com/' + 'public/' + filename
print(url)
