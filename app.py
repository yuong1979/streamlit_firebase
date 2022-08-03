import streamlit as st
import pyrebase
from firebase_admin import auth
import json
from authentication_functions import log_in, sign_up, log_out, reset_user_password, status
from streamlit_option_menu import option_menu
from sales_dashboard import sales_report
from sankey_dashboard import sankey_report
from scatterplot import scatterplot_report
from bar_chart import bar_report
from coloredbarchart import coloredbarchart

with open('secret/firebase_app_config.json') as f:
    config = json.load(f)

firebase = pyrebase.initialize_app(config) 
auth = firebase.auth()

def main():
    st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide") #layout can be centered

    # st.title("streamlit forms")

    with st.sidebar:
        selected = option_menu(
            menu_title="Main Menu",  # required
            options=["Home", 
                "Chart1", 
                "Chart2", 
                "Chart3",
                "Chart4",
                "Chart5"
                ],  # required
            icons=["house", "book", "envelope"],  # optional
            menu_icon="cast",  # optional
            default_index=0,  # optional - what option is selected by default first
        )

    if selected == "Home":
        st.title(f"You have selected {selected}")

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



    if selected == "Chart1":
        st.title(f"You have selected {selected}")
        sales_report()
        status()

    if selected == "Chart2":
        st.title(f"You have selected {selected}")
        sankey_report()
        status()

    if selected == "Chart3":
        st.title(f"You have selected {selected}")
        scatterplot_report()
        status()

    if selected == "Chart4":
        st.title(f"You have selected {selected}")
        bar_report()
        status()

    if selected == "Chart5":
        st.title(f"You have selected {selected}")
        coloredbarchart()
        status()


if __name__ == '__main__':
    main()
