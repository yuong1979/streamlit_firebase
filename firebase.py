import pyrebase
from firebase_admin import auth
import json


with open('firebase_app_config.json') as f:
    config = json.load(f)

firebase = pyrebase.initialize_app(config) 
auth = firebase.auth()


email = "yuong1979@gmail.com"
password = "123456"

# user = auth.create_user_with_email_and_password(email, password)

# user = auth.sign_in_with_email_and_password(email, password)

# # print (user['email'])
# print (user)

# #getting the id token
# idtoken = user['idToken']

# print (idtoken)

idtoken = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjFhZjYwYzE3ZTJkNmY4YWQ1MzRjNDAwYzVhMTZkNjc2ZmFkNzc3ZTYiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vcHl0aG9uLWZpcmVzdG9yZS01MmNmYyIsImF1ZCI6InB5dGhvbi1maXJlc3RvcmUtNTJjZmMiLCJhdXRoX3RpbWUiOjE2NTkyNzAwMjksInVzZXJfaWQiOiJvN2duYVBZdFl3YW1RYkxlVENKOWUzMWs5OEIyIiwic3ViIjoibzdnbmFQWXRZd2FtUWJMZVRDSjllMzFrOThCMiIsImlhdCI6MTY1OTI3MDAyOSwiZXhwIjoxNjU5MjczNjI5LCJlbWFpbCI6Inl1b25nMTk3OUBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiZmlyZWJhc2UiOnsiaWRlbnRpdGllcyI6eyJlbWFpbCI6WyJ5dW9uZzE5NzlAZ21haWwuY29tIl19LCJzaWduX2luX3Byb3ZpZGVyIjoicGFzc3dvcmQifX0.iismjltjgdLJgDo7dU5-M0CTPt7yTV6j-oq4CFfYVpMyIJ2KHD2HBfnRMzVqW9KE6Vaepb502ZpConz3mS_QmrsAoZlIXWpykDzqv3sR0RaEElv_Tuzw3y-6eulOt-7cy53sO9IOHLUBuDfinwdZdUxrOzfPfGLwW6I6FR7NJKH2uVBJli3aSmq3bU6W5jTXZg2jWJGBlhwI_DKd1Kl7COwOw6ipqf_WumdwSkqjRjzBfwsCtLeYgJr1ydegOkpL0E3JK1lcr2XIZUFkyHK4Avcj_0Q_PkeTSXYlsX72Cm_Ezca0KXzGcaS4NEEykGcZ3Yn0Al48BxObo70ZrH77kg'

userinfo = auth.get_account_info(idtoken)
print (userinfo)


# auth.refresh(user['refreshToken'])

# useremail = userinfo['users'][0]['email']
# useremailverified = userinfo['users'][0]['emailVerified']
# validSince = userinfo['users'][0]['validSince']
# lastLoginAt = userinfo['users'][0]['lastLoginAt']
# createdAt = userinfo['users'][0]['createdAt']
# lastRefreshAt = userinfo['users'][0]['lastRefreshAt']
# print (useremailverified, "useremailverified")
# print (useremail, "useremail")
# print (validSince, "validSince")
# print (lastLoginAt, "lastLoginAt")#changes based on login time
# print (createdAt, "createdAt")
# print (lastRefreshAt, "lastRefreshAt")#changes based on login time

# print (userinfo)

# userinfo = auth.get_account_info(idtoken)
# print (userinfo)

# useremailverified = userinfo['users'][0]['emailVerified']
# print (useremailverified)

# user = auth.refresh(user['refreshToken'])

# auth.send_password_reset_email(email)
# auth.delete_user_account(useridtoken)

# auth.send_email_verification(idtoken)

# user = auth.refresh(user['refreshToken'])







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
