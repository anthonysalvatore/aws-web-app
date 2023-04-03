from flask import Flask, render_template, request, redirect, url_for, flash, session
import boto3
from boto3.dynamodb.conditions import Key
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

dynamodb = boto3.resource('dynamodb')
login_table = dynamodb.Table('login')
music_table = dynamodb.Table('music')
subscriptions_table = dynamodb.Table('subscriptions')

def query_table(key, condition, table):
    response = table.query(KeyConditionExpression=Key(key).eq(condition))
    return response['Items']

def search_music(title, year, artist):
    # Define the filter expression and attribute values
    filter_expression = []
    expression_attribute_values = {}
    expression_attribute_names = {}

    if title:
        filter_expression.append('title = :title')
        expression_attribute_values[':title'] = title

    if year:
        filter_expression.append('#yr = :year')
        expression_attribute_values[':year'] = year
        expression_attribute_names['#yr'] = 'year'

    if artist:
        filter_expression.append('artist = :artist')
        expression_attribute_values[':artist'] = artist


    # Join the filter expressions with AND
    filter_expression = ' AND '.join(filter_expression)

    # Perform the scan operation (was failing if year was empty; quick fix)
    if year:
        response = music_table.scan(FilterExpression=filter_expression, ExpressionAttributeValues=expression_attribute_values, ExpressionAttributeNames=expression_attribute_names)
    else:
        response = music_table.scan(FilterExpression=filter_expression, ExpressionAttributeValues=expression_attribute_values)

    return response['Items']

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.pop('email', None)
    session.pop('userame', None)
    session.pop('query', None)

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        response = login_table.get_item(Key={'email': email})
        
        if 'Item' in response and response['Item']['password'] == password:
            # User is logged in successfully, redirect to the main page, store session info
            session['email'] = email
            session['user_name'] = response['Item']['user_name']
            return redirect(url_for('main_page'))
        else:
            flash('Email or password is invalid')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        new_user = {'email': email, 'user_name': username, 'password': password}

        response = login_table.get_item(Key={'email': email})

        if 'Item' in response and response['Item']['email'] == email:
            # Email already exists in DB, direct to retry
            flash('The email already exists')
        else:
            login_table.put_item(Item=new_user)
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/remove_subscription', methods=['POST'])
def remove_subscription():
    # If not logged in, redirect to login
    if 'email' not in session:
        return redirect(url_for('login'))

    title = request.form['subscription_title']
    response = subscriptions_table.delete_item(Key={'email': session['email'], 'title': title})
    return redirect(url_for('main_page'))

@app.route('/add_subscription', methods=['POST'])
def add_subscription():
    # If not logged in, redirect to login
    if 'email' not in session:
        return redirect(url_for('login'))

    title = request.form['add_title']
    artist = request.form['add_artist']
    year = request.form['add_year']
    img_url = request.form['add_url']

    new_subscription = {'email': session['email'], 'title': title, 'artist': artist, 'year': year, 'img_url': img_url}
    response = subscriptions_table.put_item(Item=new_subscription)
    return redirect(url_for('main_page'))

@app.route('/search', methods=['POST'])
def search():
    # Clear search query
    session.pop('query', None)

    title = request.form['title'].strip()
    artist = request.form['artist'].strip()
    year = request.form['year'].strip()

    if not title and not artist and not year:
        flash('No result is retrieved. Please query again.')
        return redirect(url_for('main_page'))

    results = search_music(title, year, artist)

    if not results:
        flash('No result is retrieved. Please query again.')
        return redirect(url_for('main_page'))

    session['query']=results

    return redirect(url_for('main_page'))

@app.route('/logout')
def logout():
    # Remove user from session, redirect to login
    session.pop('email', None)
    session.pop('userame', None)
    session.pop('query', None)
    
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def main_page():
    # If not logged in, redirect to login
    if 'email' not in session:
        return redirect(url_for('login'))
    
    user_name = session['user_name']     
    query = session.get('query',[])

    subscriptions = query_table('email', session['email'], subscriptions_table)

    return render_template('main.html', user_name=user_name, subscriptions=subscriptions, query=query)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)