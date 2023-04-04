from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

api_url = 'https://btki7ax6b3.execute-api.us-east-1.amazonaws.com/beta/app-actions'

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.pop('email', None)
    session.pop('userame', None)
    session.pop('query', None)

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        data = {
            'action': "get_user",
            'email': email
        }
        response = requests.post(api_url, json=data)
        response_data = response.json()['body']
        
        if 'Item' in response_data and response_data['Item']['password'] == password:
            # User is logged in successfully, redirect to the main page, store session info
            session['email'] = email
            session['user_name'] = response_data['Item']['user_name']
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

        new_user = {'action': 'create_user', 'email': email, 'user_name': username, 'password': password}

        data = {
            'action': "get_user",
            'email': email
        }
        response = requests.post(api_url, json=data)
        response_data = response.json()['body']

        if 'Item' in response_data and response_data['Item']['email'] == email:
            # Email already exists in DB, direct to retry
            flash('The email already exists')
        else:
            response = requests.post(api_url, json=new_user)
            return redirect(url_for('login'))


    return render_template('register.html')

@app.route('/remove_subscription', methods=['POST'])
def remove_subscription():
    # If not logged in, redirect to login
    if 'email' not in session:
        return redirect(url_for('login'))

    title = request.form['subscription_title']

    data = {
        'action': "delete_subscription",
        'email': session['email'],
        'title': title
    }
    requests.post(api_url, json=data)
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

    new_subscription = {'action':"create_subscription", 'email': session['email'], 'title': title, 'artist': artist, 'year': year, 'img_url': img_url}
    response = requests.post(api_url,json=new_subscription)
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

    data = {'action': "search_music",}
    if title: data['title'] = title
    if artist: data['artist'] = artist
    if year: data['year'] = year

    response = requests.post(api_url, json=data)
    response_data = response.json()['body']

    if not response_data['Items']:
        flash('No result is retrieved. Please query again.')
        return redirect(url_for('main_page'))

    session['query']=response_data['Items']

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

    data = {
        'action': "get_subscriptions",
        'email': session['email']
    }
    response = requests.post(api_url, json=data)
    response_data = response.json()['body']
    subscriptions = response_data['Items']

    return render_template('main.html', user_name=user_name, subscriptions=subscriptions, query=query)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)