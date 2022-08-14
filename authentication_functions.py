import streamlit as st
import requests
from firebase_admin import auth
import json
# from streamlit.components.v1 import html
import pyrebase
import requests
from secret import access_secret
import json
from settings import project_id, firebase_database, fx_api_key, firestore_api_key, google_sheets_api_key, schedule_function_key, firebase_auth_api_key



firebase_auth_api_key = access_secret(firebase_auth_api_key, project_id)
firebase_auth_api_key_dict = json.loads(firebase_auth_api_key)

firebase = pyrebase.initialize_app(firebase_auth_api_key_dict) 
auth = firebase.auth()

def log_in():
    email = st.session_state.login_email
    password = st.session_state.login_password
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        idtoken = user['idToken']
        userinfo = auth.get_account_info(idtoken)
        useremailverified = userinfo['users'][0]['emailVerified']
        if useremailverified == True:
            st.session_state['authenticated'] = True
            st.session_state['email'] = userinfo['users'][0]['email']
            st.session_state['user'] = user
            st.success("{} is signed in ".format(email))
        else:
            #send email to user to verify email
            auth.send_email_verification(user['idToken'])
            st.error("Hello {}, please verify your email first, we have sent you an email".format(email))

    except requests.HTTPError as e:
        error_json = e.args[1]
        error = json.loads(error_json)['error']['message']
        st.error(error)

    except Exception as e:
        st.error(e)





def log_out():
    del st.session_state["user"]
    st.session_state['authenticated'] = False

def sign_up():
    email = st.session_state.signup_email
    password = st.session_state.signup_password

    try:
        user = auth.create_user_with_email_and_password(email, password)
        auth.send_email_verification(user['idToken'])
        st.success("Hello {}, we have sent an email to you, please check and confirm".format(email))

    except requests.HTTPError as e:
        error_json = e.args[1]
        error = json.loads(error_json)['error']['message']
        st.error(error)

    except Exception as e:
        st.error(e)

def reset_user_password():
    try:
        email = st.session_state.reset_email_password
        auth.send_password_reset_email(email)
        st.success("Hello {}, we have sent an email to you, please click on the validation link".format(email))

    except requests.HTTPError as e:
        error_json = e.args[1]
        error = json.loads(error_json)['error']['message']
        st.error(error)

    except Exception as e:
        st.error(e)


def status():

    try:
        user = st.session_state['user']
        userinfo = auth.get_account_info(user['idToken'])
        if userinfo['users'][0]['emailVerified'] == True:
            st.session_state['authenticated'] = True    
            auth.refresh(user['refreshToken'])
            useremail = userinfo['users'][0]['email']
            st.write("{} is logged in".format(useremail))
    except:
        st.session_state['authenticated'] = False
        st.write("User is not logged in")