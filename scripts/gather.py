import json
import pyrebase

# Set up firebase database
config = json.load(open("scripts/config.json"))
firebase = pyrebase.initialize_app(config)
db = firebase.database()

# get users
print(db.child("users").get().val())

# get mixes
print(db.child("mixes").get().val())