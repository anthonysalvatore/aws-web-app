import boto3
import json
import requests
from io import BytesIO

s3 = boto3.client('s3')
bucket_name = 's3920301-music'

try:
    s3.create_bucket(Bucket=bucket_name)
except Exception as e:
    print(e)
    print('Connection to AWS could not be established or bucket name already exists.')

with open('aws-web-app/a1.json', 'r') as json_file:
    data = json.load(json_file)

for item in data['songs']:
    img_url = item['img_url']
    response = requests.get(img_url)
    s3.upload_fileobj(BytesIO(response.content), bucket_name, f"images/{item['artist']}.jpg")

print("Artist images have been uploaded to S3.")
