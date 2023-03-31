import json
import boto3

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb')
# Link to music table
table = dynamodb.Table('music')

with open('aws-web-app/a1.json', 'r') as json_file:
    data = json.load(json_file)

for item in data['songs']:
    table.put_item(Item=item)

print("All items have successfully been loaded into the 'music' table.")