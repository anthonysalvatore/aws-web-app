import boto3
from boto3.dynamodb.conditions import Key
import os
import json

dynamodb = boto3.resource('dynamodb')
login_table = dynamodb.Table('login')
music_table = dynamodb.Table('music')
subscriptions_table = dynamodb.Table('subscriptions')

def lambda_handler(event, context):
    action = event['action']
    if action == 'create_user':
        return create_user(event)
    elif action == 'get_user':
        return get_user(event)
    elif action == 'create_subscription':
        return create_subscription(event)
    elif action == 'delete_subscription':
        return delete_subscription(event)
    elif action == 'get_subscriptions':
        return get_subscriptions(event)
    elif action == 'search_music':
        return search_music(event)
    else:
        return {'statusCode': 400, 'body': 'Invalid action'}

def create_user(event):
    response = login_table.put_item(
        Item={
            'email': event['email'],
            'user_name': event['user_name'],
            'password': event['password'],
        }
    )
    return {'statusCode': 200, 'body': 'User created'}

def get_user(event):
    response = login_table.get_item(
        Key={
            'email': event['email']
        }
    )
    return {'statusCode': 200, 'body': response}

def create_subscription(event):
    response = subscriptions_table.put_item(
        Item={
            'email': event['email'], 
            'title': event['title'], 
            'artist': event['artist'], 
            'year': event['year'], 
            'img_url': event['img_url']
            }
    )
    return {'statusCode': 200, 'body': 'Subscription created'}

def delete_subscription(event):
    response = subscriptions_table.delete_item(
        Key={
            'email': event['email'],
            'title': event['title']
        }
    )
    return {'statusCode': 200, 'body': 'Subscription deleted'}

def get_subscriptions(event):
    response = subscriptions_table.query(KeyConditionExpression=Key('email').eq(event['email']))
    return {'statusCode': 200, 'body': response}

def search_music(event):
    # Define the filter expression and attribute values
    filter_expression = []
    expression_attribute_values = {}
    expression_attribute_names = {}

    if 'title' in event:
        filter_expression.append('title = :title')
        expression_attribute_values[':title'] = event['title']

    if 'year' in event:
        filter_expression.append('#yr = :year')
        expression_attribute_values[':year'] = event['year']
        expression_attribute_names['#yr'] = 'year'

    if 'artist' in event:
        filter_expression.append('artist = :artist')
        expression_attribute_values[':artist'] = event['artist']


    # Join the filter expressions with AND
    filter_expression = ' AND '.join(filter_expression)

    # Perform the scan operation (was failing if year was empty; quick fix)
    if 'year' in event:
        response = music_table.scan(FilterExpression=filter_expression, ExpressionAttributeValues=expression_attribute_values, ExpressionAttributeNames=expression_attribute_names)
    else:
        response = music_table.scan(FilterExpression=filter_expression, ExpressionAttributeValues=expression_attribute_values)

    return {'statusCode': 200, 'body': response}