from flask import Flask, render_template, request, redirect, url_for, flash, session
import boto3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

dynamodb = boto3.resource('dynamodb')
login_table = dynamodb.Table('login')

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

        respone = login_table.get_item(Key={'email': email})

        if 'Item' in response and response['Item']['password'] == password:
            # Email already exists in DB, direct to retry
            flash('The email already exists')
        else:
            login_table.put_item(Item=new_user)
            redirect(url_for('login'))

    return render_template('register.html')

@app.route('/')
def main_page():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    user_name = session['user_name']

    return render_template('main.html', user_name=user_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)