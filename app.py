from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
import os

app = Flask(__name__)
app.secret_key = b'U\xdaZ\xb0)\xd6`#\xb6\x18\x05\x1eT\x93\xe3\x98\xdao"\xbe\x92\x89\xb0o'

# API url to connect to API gateway
api_url = 'https://btki7ax6b3.execute-api.us-east-1.amazonaws.com/beta/app-actions'

# Logging in
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Clear session data
    session.pop('email', None)
    session.pop('userame', None)
    session.pop('query', None)

    # Process form submission
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Prepare data to send to API for user retrieval
        data = {
            'action': "get_user",
            'email': email
        }
        # Send request to API
        response = requests.post(api_url, json=data)
        response_data = response.json()['body']
        
        # Check if user exists and password is correct
        if 'Item' in response_data and response_data['Item']['password'] == password:
            # User is logged in successfully, redirect to the main page, store session info
            session['email'] = email
            session['user_name'] = response_data['Item']['user_name']
            return redirect(url_for('main_page'))
        else:
            flash('Email or password is invalid')
    
    # Render login template
    return render_template('login.html')

# Registering new users
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Process form submission
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # Prepare data for creating a new user
        new_user = {'action': 'create_user', 'email': email, 'user_name': username, 'password': password}

        # Prepare data to check if the user already exists
        data = {
            'action': "get_user",
            'email': email
        }
        # Send request to API
        response = requests.post(api_url, json=data)
        response_data = response.json()['body']

        # Check if email already exists in the database
        if 'Item' in response_data and response_data['Item']['email'] == email:
            # Email already exists in DB, direct to retry
            flash('The email already exists')
        else:
            # Create a new user
            response = requests.post(api_url, json=new_user)
            return redirect(url_for('login'))

    # Render register template
    return render_template('register.html')

# Remove a particular subscription from subscription table
@app.route('/remove_subscription', methods=['POST'])
def remove_subscription():
    # If not logged in, redirect to login
    if 'email' not in session:
        return redirect(url_for('login'))

    # Get subscription title from form
    title = request.form['subscription_title']

    # Prepare data to send to API for subscription removal
    data = {
        'action': "delete_subscription",
        'email': session['email'],
        'title': title
    }
    # Send request to API
    requests.post(api_url, json=data)
    return redirect(url_for('main_page'))

# Add a subscription from query to subscription table
@app.route('/add_subscription', methods=['POST'])
def add_subscription():
    # If not logged in, redirect to login
    if 'email' not in session:
        return redirect(url_for('login'))

    # Get subscription details from form
    title = request.form['add_title']
    artist = request.form['add_artist']
    year = request.form['add_year']
    img_url = request.form['add_url']

    # Prepare data for creating a new subscription
    new_subscription = {'action':"create_subscription", 'email': session['email'], 'title': title, 'artist': artist, 'year': year, 'img_url': img_url}
    # Send request to API
    response = requests.post(api_url,json=new_subscription)
    return redirect(url_for('main_page'))

# Scan music table for matches to title/artist/year
@app.route('/search', methods=['POST'])
def search():
    # Clear search query
    session.pop('query', None)

    # Get query details from form
    title = request.form['title'].strip()
    artist = request.form['artist'].strip()
    year = request.form['year'].strip()

    # If no input, display a message and redirect to main page
    if not title and not artist and not year:
        flash('No result is retrieved. Please query again.')
        return redirect(url_for('main_page'))

    # Prepare data for searching music
    data = {'action': "search_music",}
    if title: data['title'] = title
    if artist: data['artist'] = artist
    if year: data['year'] = year

    # Send request to API
    response = requests.post(api_url, json=data)
    response_data = response.json()['body']

    # If no results found, display a message and redirect to main page
    if not response_data['Items']:
        flash('No result is retrieved. Please query again.')
        return redirect(url_for('main_page'))

    # Store query results in session
    session['query']=response_data['Items']

    return redirect(url_for('main_page'))

# Logout
@app.route('/logout')
def logout():
    # Remove user from session, redirect to login
    session.pop('email', None)
    session.pop('userame', None)
    session.pop('query', None)
    
    return redirect(url_for('login'))

# Main page, user area, subscription area, query area
@app.route('/', methods=['GET', 'POST'])
def main_page():
    # If not logged in, redirect to login
    if 'email' not in session:
        return redirect(url_for('login'))
    
    # User area
    user_name = session['user_name']     
    query = session.get('query',[])

    # Prepare data for retrieving subscriptions
    data = {
        'action': "get_subscriptions",
        'email': session['email']
    }
    # Send request to API
    response = requests.post(api_url, json=data)
    response_data = response.json()['body']
    subscriptions = response_data['Items']

    return render_template('main.html', user_name=user_name, subscriptions=subscriptions, query=query)

if __name__ == '__main__':
    app.run(host='0.0.0.0')