import streamlit as st
import pandas as pd

import pyrebase
from firebase_admin import auth
import json



# test = st.session_state
# st.write(test)
# email = 'testing@gmail.com'
# st.session_state['email'] = email
# st.write(test)
# if 'testing@gmail.com' in st.session_state['email']:
#     st.write("user logged in")



# def form_callback():
#     st.write(st.session_state.my_slider)
#     st.write(st.session_state.my_checkbox)

# with st.form(key='my_form'):
#     slider_input = st.slider('My slider', 0, 10, 5, key='my_slider')
#     checkbox_input = st.checkbox('Yes or No', key='my_checkbox')
#     submit_button = st.form_submit_button(label='Submit', on_click=form_callback)



a = st.radio("", ['Login', 'Signup'], 0, horizontal=True)
if a == 'Login':
    st.subheader("Log In")
    with st.form(key="SignUpForm"):
        email = st.text_input("Enter your Email")
        password = st.text_input("Enter a password", type="password")
        submit_button = st.form_submit_button(label="Login")
else:
    st.subheader("Sign Up")
    with st.form(key="SignUpForm"):
        email = st.text_input("Enter your Email")
        password = st.text_input("Enter a password", type="password")
        submit_button = st.form_submit_button(label="Sign up")