from argon2 import hash_password
import streamlit_authenticator as stauth
import database as db
import bcrypt

usernames = ["pparker", "rmiller"]
names = ["Peter Parker", "Rebecca Miller"]
passwords = ["abc123", "def456"]

hashed_passwords = stauth.Hasher(passwords).generate()

## Tried hashing and inserting using bcrypt but the DETAbase doesnt take in json format and if I encode it is in json format
# hashed_passwords = []
# for i in passwords:
#     i = bcrypt.hashpw(i.encode("utf-8"), bcrypt.gensalt())
#     hashed_passwords.append(i)

print (usernames)
print (names)
print (hashed_passwords)

for (username, name, hashed_password) in zip(usernames, names, hashed_passwords):
    db.insert_user(username, name, hashed_password)


