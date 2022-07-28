import pyrebase
from firebase_admin import auth
from flask import Flask, session, render_template, request, redirect
import json


app = Flask(__name__)

with open('config.json') as f:
    config = json.load(f)

firebase = pyrebase.initialize_app(config) 
auth = firebase. auth()

app.secret_key = 'secret'

@app.route('/', methods=['POST', 'GET']) 
def index():
    print (session)
    if ('user' in session):
        print ("user in session")
        return 'Hi, {}'.format(session['user'])
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            print ("signed in")
            session['user'] = email
        except:
            print ("failed")
            return 'Failed to login'
    return render_template('home.html')

@app.route('/logout') 
def logout():
    session.pop('user')
    print ('logged out')
    return redirect('/')

if __name__ == '__main__':
    app.run(port=1111)




# email = "test2@gmail.com"
# password = "123456"

# ## for creating new user data on new account
# user = auth.create_user_with_email_and_password(email, password)
# print (user)

# ## for retriveving user data
# info = auth.get_account_info(user['idToken'])
# print (info)

# ## email verification
# auth.send_email_verification(user['idToken'])

# ## for password reset
# auth.send_password_reset_email(email)

# ## list of methods inside auth
# # 'api_key', 'create_custom_token', 'create_user_with_email_and_password', 'credentials', 'current_user', 'delete_user_account', 'get_account_info', 'refresh', 'requests', 'send_email_verification', 'send_password_reset_email', 'sign_in_anonymous', 'sign_in_with_custom_token', 'sign_in_with_email_and_password', 'verify_password_reset_code'

# Based on a tutorial by https://youtu.be/HltzFtn9f1c