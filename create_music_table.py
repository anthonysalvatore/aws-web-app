import boto3

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb')

# Define schema, attributes and throughput of new table
table = dynamodb.create_table(
    TableName='music',
    KeySchema=[
        {
            'AttributeName': 'title',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'artist',
            'KeyType': 'RANGE'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'title',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'artist',
            'AttributeType': 'S'
        },
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

# Wait until table exists within DB, print msg when ready
table.meta.client.get_waiter('table_exists').wait(TableName='music')
print("Table 'music' is ready.")


