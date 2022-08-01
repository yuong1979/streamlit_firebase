import streamlit as st
import pandas as pd
import requests
import pyrebase
from firebase_admin import auth
import json
from streamlit.components.v1 import html

with open('firebase_app_config.json') as f:
    config = json.load(f)

firebase = pyrebase.initialize_app(config) 
auth = firebase. auth()

def main():

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


    st.title("streamlit forms")
    menu = ["Home", "About"]
    choice = st.sidebar.selectbox("Menu", menu )

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




    if choice == "Home":

        if st.session_state['authenticated'] == False:

            a = st.radio("", ['Login', 'Signup', 'Reset Email'], 0, horizontal=True)
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
            submit_button = st.button(label="Logout", on_click=log_out)

            status()

    else:
        st.subheader("About")

        status()



if __name__ == '__main__':
    main()
