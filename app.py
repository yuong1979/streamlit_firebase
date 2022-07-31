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
        user = auth.sign_in_with_email_and_password(email, password)
        del st.session_state["login_password"]
        del st.session_state["login_email"]

        idtoken = user['idToken']
        userinfo = auth.get_account_info(idtoken)
        useremailverified = userinfo['users'][0]['emailVerified']
        if useremailverified == True:
            st.session_state['authenticated'] = True
            st.session_state['email'] = userinfo['users'][0]['email']
            # st.session_state['idtoken'] = idtoken
            st.session_state['user'] = user
            st.write("User is signed in ".format(email))
        else:
            #send email to user to verify email
            auth.send_email_verification(user['idToken'])
            st.write("Hey {}, please verify your email first, we have sent you an email".format(email))

    def log_out():
        # del st.session_state["idtoken"]
        del st.session_state["user"]
        st.session_state['authenticated'] = False
        try:
            del st.session_state["email"]
        except:
            pass

    def sign_up():
        email = st.session_state.signup_email
        password = st.session_state.signup_password
        user = auth.create_user_with_email_and_password(email, password)
        del st.session_state["signup_email"]
        del st.session_state["signup_password"]
        # useridtoken = user['idToken']
        auth.send_email_verification(user['idToken'])
        st.success("Hello {}, we have sent an email to you, please check and confirm".format(email))



    def status():
        try:
            user = st.session_state['user']
            #include refreshing of the cookie to extent logging in
            auth.refresh(user['refreshToken'])
            userinfo = auth.get_account_info(user['idtoken'])
            useremail = userinfo['users'][0]['email']
            st.write("{} is logged in".format(useremail))
        except:
            st.session_state['authenticated'] = False
            st.write("User is not logged in")


    st.title("streamlit forms")
    menu = ["Home", "About"]
    choice = st.sidebar.selectbox("Menu", menu )

    "st.session_state object:", st.session_state

    if 'user' in st.session_state.keys():
        st.session_state['authenticated'] = True
    else:
        st.session_state['authenticated'] = False




    if choice == "Home":

        if st.session_state['authenticated'] == False:

            a = st.radio("", ['Login', 'Signup', 'Reset Email'], 0, horizontal=True)
            if a == 'Login':


                st.subheader("Log In")
                with st.form(key="SignInForm"):
                    email = st.text_input("Enter your Email", key="login_email")
                    password = st.text_input("Enter a password", type="password", key="login_password")
                    submit_button = st.form_submit_button(label="Login", on_click=log_in)

            elif a == 'Signup':
                st.subheader("Sign Up")
                with st.form(key="SignUpForm"):
                    email = st.text_input("Enter your Email", key="signup_email")
                    password = st.text_input("Enter a password", type="password", key="signup_password")
                    submit_button = st.form_submit_button(label="Sign up", on_click=sign_up)

            else:

                st.subheader("Reset Email")
                with st.form(key="ResetEmail"):
                    email = st.text_input("Enter your Email")
                    submit_button = st.form_submit_button(label="Reset")

                    if submit_button:
                        try:
                            auth.send_password_reset_email(email)
                            st.success("Hello {}, we have sent an email to you, please check and confirm".format(email))
                        except:
                            return 'Failed to send'

        else:
            submit_button = st.button(label="Logout", on_click=log_out)

            status()

    else:
        st.subheader("About")

        status()



if __name__ == '__main__':
    main()
