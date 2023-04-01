from flask import Flask, render_template, request, redirect, url_for, flash
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
            # User is logged in successfully, redirect to the main page
            return redirect(url_for('main_page'))
        else:
            flash('Email or password is invalid')
    
    return render_template('login.html')

@app.route('/register')
def register():
    return 'Registration'

@app.route('/')
def main_page():
    return 'Main page'

if __name__ == '__main__':
    app.run(host='0.0.0.0')