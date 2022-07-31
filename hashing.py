import bcrypt

#this process encodes the password
# password = 'SecretPassword'
# password = password.encode("utf-8")

#this is similar to the above - which encodes the password
password = b'SecretPassword'
hashed = bcrypt.hashpw(password, bcrypt.gensalt())

if bcrypt.checkpw(password, hashed):
    print ("password match")
else:
    print ("password not match")

