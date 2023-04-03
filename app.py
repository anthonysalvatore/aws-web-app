from flask import Flask, render_template, request, redirect, url_for, flash, session
import boto3
from boto3.dynamodb.conditions import Key
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

dynamodb = boto3.resource('dynamodb')
login_table = dynamodb.Table('login')
subscriptions_table = dynamodb.Table('subscriptions')

def query_table(key, condition, table):
    response = table.query(KeyConditionExpression=Key(key).eq(condition))
    return response['Items']

@app.route('/login', methods=['GET', 'POST'])
def login():
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

#@app.route('/remove_subscription')
#def remove_subscription():
#    pass

@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('userame', None)
    
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def main_page():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    user_name = session['user_name']

    if request.method == 'POST':
        title = request.form['subscription_title']
        response = subscriptions_table.delete_item(Key={'email': session['email'], 'title': title})

    subscriptions = query_table('email', session['email'], subscriptions_table)

    return render_template('main.html', user_name=user_name, subscriptions=subscriptions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)