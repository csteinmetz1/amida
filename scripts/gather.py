import os
import json
import pyrebase

# Set up firebase database
config = json.load(open("scripts/config.json"))
firebase = pyrebase.initialize_app(config)
db = firebase.database()

# create directory for storing data
data_dir = "scripts/data"
if not os.path.isdir(data_dir):
	os.makedirs(data_dir)

# grab latest data from the database
users = db.child("users").get().val()	# get users
mixes = db.child("mixes").get().val()	# get mixes

# save data to json files
with open(os.path.join(data_dir, "users.json"), 'w') as fp:
	json.dump(users, fp, indent=2)

with open(os.path.join(data_dir, "mixes.json"), 'w') as fp:
	json.dump(mixes, fp, indent=2)
