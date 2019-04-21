import os
import json
import numpy as np
import matplotlib.pyplot as plt

# useful constants, details, and configuration
data_dir = "scripts/data"
stems = ["drums", "bass", "other", "vocals"]
songs = np.arange(1, 101)

# load .json files
try:
	with open(os.path.join(data_dir, "users.json"), 'r') as fp:
		users = json.load(fp)

	with open(os.path.join(data_dir, "mixes.json"), 'r') as fp:
		mixes = json.load(fp)
except:
	print("Database files not found. Run gather.py to get latest data.\n")

# -----------------------------------------------------------------------------
# find the mean mix coefficients across all songs
# -----------------------------------------------------------------------------
overall_mixes = []
for stem in stems:
	# for analysis here we don't plot stems that were mixes to -80 dB (or silent)
	overall_mixes.append([m[stem] for k, m in mixes.items() if m[stem] > -80])

# create box plot for stems across all songs
fig, ax = plt.subplots(1, figsize=(6,4))
bp = ax.boxplot(overall_mixes)
ax.set_xticklabels(stems)
ax.set_title("Level settings across all mixes")
ax.set_ylabel("Gain (dB)")
plt.show()
plt.cla()

# -----------------------------------------------------------------------------
# find the mean mix coefficients for each song by stem type
# -----------------------------------------------------------------------------
for stem in stems:
	all_mixes = []
	for song in songs:
		all_mixes.append([m[stem] for k, m in mixes.items() if m["songId"] == song and m[stem] > -80])

	# create box plot for stems across all songs
	fig, ax = plt.subplots(1, figsize=(20,4))
	bp = ax.boxplot(all_mixes)
	ax.set_xticklabels(songs)
	plt.xticks(rotation=90)
	ax.set_title(f"{stem} level across all mixes")
	ax.set_ylabel("Gain (dB)")
	plt.show()
