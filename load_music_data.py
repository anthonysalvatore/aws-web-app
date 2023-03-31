import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('music')

with open('a1.json', 'r') as json_file:
    data = json.load(json_file)

for item in data:
    table.put_item(Item=item)

print("All items have successfully been loaded into the 'music' table.")