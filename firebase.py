import pyrebase
from firebase_admin import auth
import json
import re

with open('firebase_app_config.json') as f:
    config = json.load(f)

firebase = pyrebase.initialize_app(config) 
auth = firebase.auth()

txt = "The rain { smoking now hahaha  in Spain }"
s = 'Part 1. Part 2. Part 3 then more text'
test1 = re.search(r'Part 1\.(.*?)Part 3', s).group(1)
test2 = re.search(r'Part 1(.*?)Part 3', s).group(1)
test3 = re.search(r'{(.*?)}', txt).group(1)
print(test3)

# txt = "The rain in Spain"
# x = re.search("^The.*Spain$", txt).group()

# print(x)


email = "yuong1979@gmail.com"
password = "qwer1234"

# user = auth.create_user_with_email_and_password(email, password)

# user = auth.sign_in_with_email_and_password(email, password)

# # print (user['email'])
# print (user)

# #getting the id token
# idtoken = user['idToken']

# print (idtoken)

# idtoken = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjFhZjYwYzE3ZTJkNmY4YWQ1MzRjNDAwYzVhMTZkNjc2ZmFkNzc3ZTYiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vcHl0aG9uLWZpcmVzdG9yZS01MmNmYyIsImF1ZCI6InB5dGhvbi1maXJlc3RvcmUtNTJjZmMiLCJhdXRoX3RpbWUiOjE2NTkzMTcwNjYsInVzZXJfaWQiOiJMMTc0VjJiaTJZWHFkV3I2U09KN28wZTRyZ3QxIiwic3ViIjoiTDE3NFYyYmkyWVhxZFdyNlNPSjdvMGU0cmd0MSIsImlhdCI6MTY1OTMxNzA2NiwiZXhwIjoxNjU5MzIwNjY2LCJlbWFpbCI6Inl1b25nMTk3OUBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiZmlyZWJhc2UiOnsiaWRlbnRpdGllcyI6eyJlbWFpbCI6WyJ5dW9uZzE5NzlAZ21haWwuY29tIl19LCJzaWduX2luX3Byb3ZpZGVyIjoicGFzc3dvcmQifX0.jII_4N7N8AkLBE8_mfb1yfhTXxRxdHdNL25vo14u53RvbI0duhEta1sceCnXEeTPTSo3UQtwShn31xBLczcndAtd8GyFSV2pfwOu7cHNnv0YpSagrdxj1A9l5HO5glWe0Wgbd28Ye6TUqgZkYj_Zse4KYZVyJhzVNaSqKb-2pll0HcaL6_GXs_mLNpAu0N2aqdY70kmGcTP8nxFZccnQ9x4KVNl4JeA0zeiug_nNafCnEI7FyBYRAcc8fAyngMjxfXsgwGDCt04AkR2CktoaN6IrpJxNsmSG_BOuuzKDtZ2RLY1p8Ko3w3bckM6mH0k_UgkmHtR63-pFjaNVatngNQ'

# userinfo = auth.get_account_info(idtoken)
# print (userinfo)



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


# auth.send_password_reset_email(useremail)
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
