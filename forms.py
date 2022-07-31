import streamlit as st
import pandas as pd


def main():
    st.title("streamlit forms")
    menu = ["Home", "About"]
    choice = st.sidebar.selectbox("Menu", menu )

    if choice == "Home":
        st.subheader("Forms Tutorial")

        #Salary calculator
        with st.form(key='salaryform'):
            col1, col2, col3 = st.columns([2,2,2])
            with col1:
                amount = st.number_input("Hourly rate in $")
            with col2:
                hour_per_week = st.number_input("Hours per week", 1, 120)
            with col3:
                st.text("Salary")
                submit_salary = st.form_submit_button(label="calculate")

        if submit_salary:
            with st.expander("Results"):
                daily = [amount * 5]
                weekly = [amount * hour_per_week]
                df = pd.DataFrame({'hourly':amount, 'daily':daily, 'weekly':weekly})
                st.dataframe(df)



        # method 1
        with st.form(key="form1"):
            firstname = st.text_input("Firstname")
            firstname = st.text_input("Lastname")
            password = st.text_input("Enter a password", type="password")
            dob = st.date_input("Date of Birth")
            others = st.text_area("Describe yourself")
            submit_button = st.form_submit_button(label="Sign up now")

        if submit_button:
            st.success("Hello {} you have created an account".format(firstname))

        # method 2
        form2 = st.form(key='form2')
        username = form2.text_input("Username")
        jobtype = form2.selectbox("Job", ["Dev", "Data scientist", "Doctor"])
        submit_button = form2.form_submit_button("Login")

        if submit_button:
            st.write(username.upper())


    else:
        st.subheader("About")

if __name__ == '__main__':
    main()
