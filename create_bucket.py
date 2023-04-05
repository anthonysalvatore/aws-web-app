import boto3
import json
import requests
from io import BytesIO

# Connect to S3
s3 = boto3.client('s3')
bucket_name = 's3920301-music'

# Try create, exception if fail
try:
    s3.create_bucket(Bucket=bucket_name)
except Exception as e:
    print(e)
    print('Connection to AWS could not be established or bucket name already exists.')

# Open a1.json, load image urls, upload to S3
with open('aws-web-app/a1.json', 'r') as json_file:
    data = json.load(json_file)

for item in data['songs']:
    img_url = item['img_url']
    response = requests.get(img_url)
    # Upload as fileobj using BytesIO so don't have to temporarily store each file locally
    s3.upload_fileobj(BytesIO(response.content), bucket_name, f"{item['artist']}.jpg", ExtraArgs={'ContentType': 'image/jpeg'})

print("Artist images have been uploaded to S3.")
