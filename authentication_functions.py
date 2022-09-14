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
import streamlit as st
import json
import pyrebase
from secret import access_secret

firebase_auth_api_key = access_secret(firebase_auth_api_key, project_id)
firebase_auth_api_key_dict = json.loads(firebase_auth_api_key)
firebase = pyrebase.initialize_app(firebase_auth_api_key_dict) 
auth = firebase.auth()










def home():

    # st.title(f"Please log in to access")

    # st.subheader(f"More features coming, stay tuned...")

    "st.session_state object:", st.session_state

    #checking if user token is in session, if not user is not authenticated
    if 'user' in st.session_state.keys():
        user = st.session_state['user']
        userinfo = auth.get_account_info(user['idToken'])
        #checking if user has email verified, if not user is not authenticated
        if userinfo['users'][0]['emailVerified'] == False:
            st.session_state['authenticated'] = False
        else:    
            st.session_state['authenticated'] = True
    else:
        st.session_state['authenticated'] = False


    if st.session_state['authenticated'] == False:

        buffer, col2, buffer = st.columns([2,4,2])

        with col2:

            a = st.radio("", ['Login', 'Signup', 'Reset Email'], 0, key="authentication", horizontal=True)
            if a == 'Login':
                st.subheader("Log In")
                with st.form(key="SignInForm", clear_on_submit=True):
                    email = st.text_input("Enter your Email", key="login_email")
                    password = st.text_input("Enter a password", type="password", key="login_password")
                    submit_button = st.form_submit_button(label="Log in", on_click=log_in)

            elif a == 'Signup':
                st.subheader("Sign Up")
                with st.form(key="SignUpForm", clear_on_submit=True):
                    email = st.text_input("Enter your Email", key="signup_email")
                    password = st.text_input("Enter a password", type="password", key="signup_password")
                    submit_button = st.form_submit_button(label="Sign up", on_click=sign_up)
            else:
                st.subheader("Reset Email")
                with st.form(key="ResetEmail", clear_on_submit=True):
                    email = st.text_input("Enter your Email", key="reset_email_password")
                    submit_button = st.form_submit_button(label="Reset", on_click=reset_user_password)

    else:
        st.title(f"Your Dashboard")
        st.subheader(f"More features coming, please stay tuned...")
        submit_button = st.button(label="Logout", on_click=log_out)










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


    col1, col2, col3 = st.columns(3)

    with col1:
        st.write('')
    with col2:
        st.write('')
    with col3:
        status_container = st.container()

    

    try:
        user = st.session_state['user']
        userinfo = auth.get_account_info(user['idToken'])
        if userinfo['users'][0]['emailVerified'] == True:
            st.session_state['authenticated'] = True    
            auth.refresh(user['refreshToken'])
            useremail = userinfo['users'][0]['email']
            # st.write("{} is logged in".format(useremail))
            display_status = "{} is logged in".format(useremail)
            status_container.write(display_status)
    except:
        st.warning('Please log in')
        # home()
        st.session_state['authenticated'] = False
        # st.write("User is not logged in")
        display_status = "User is not logged in"
        # exiting to stop user from accessing the relevant data/charts
        st.stop()




