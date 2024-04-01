from flask import Flask, request
from flask import render_template, url_for ,redirect
from flask_login import UserMixin
import json
from flask_login import LoginManager, login_user, login_required, logout_user
import os 
from dotenv import load_dotenv
load_dotenv()


class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

users = {'admin': User(id='admin', username=os.getenv('ADMIN_USERNAME'), password=os.getenv('ADMIN_PASSWORD'))}

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_APP_SECRET_KEY')  # Use the secret key from the environment variable

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username, None)
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('update_client_details'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/updateclientDetails', methods=['GET', 'POST'])
@login_required

def update_client_details():
    
       # Read the existing JSON data
    with open('config.json', 'r') as file:
        data = json.load(file)

    # Initialize client_name at the start of the function
    client_name = request.form.get('client_name', None)

    if request.method == 'POST':
        if 'new_client_name' in request.form:  # Check if adding a new client
            new_client = {
                'appname': request.form['appname'],
                'appsource': request.form['appsource'],
                'userid': request.form['userid'],
                'password': request.form['password'],
                'userkey': request.form['userkey'],
                'enckey': request.form['enckey'],
                'clientcode': request.form['clientcode'],
                'pin': request.form['pin'],
                'totp': request.form['totp'],
                'qty': request.form['qty']  # Quantity can be set when adding a new client
            }
            data[request.form['new_client_name']] = new_client
        elif 'update_symbol' in request.form:
            # Update the clientsymbol for a client
            new_symbol = request.form.get('clientsymbol', '').strip()
            if client_name and client_name in data:
                data[client_name]['clientsymbol'] = new_symbol
        else:
            # Update the qty value for a client
            client_name = request.form['client_name']
            new_qty = request.form['new_qty']
            if client_name in data:
                data[client_name]['qty'] = new_qty

        # Write the updated data back to the file
        with open('config.json', 'w') as file:
            json.dump(data, file, indent=4)

    clients = list(data.keys())  # Extracting client names
    return render_template('update_client_details.html', clients=data)

@app.route('/deleteclient/<client_name>', methods=['POST'])
@login_required
def delete_client(client_name):
    with open('config.json', 'r') as file:
        data = json.load(file)
    
    # Remove the client from the dictionary
    data.pop(client_name, None)
    
    # Write the updated data back to the file
    with open('config.json', 'w') as file:
        json.dump(data, file, indent=4)
    
    # Redirect back to the client details page
    return redirect(url_for('update_client_details'))

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=80)
