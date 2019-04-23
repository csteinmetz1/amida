import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt

# useful constants, details, and configuration
data_dir = "scripts/data"
plot_dir = "plots"
plot_type = ".png"
stems = ["drums", "bass", "other", "vocals"]
songs = np.arange(1, 101)

# create output directory
if not os.path.isdir(plot_dir):
	os.makedirs(plot_dir)

# load .json files
try:
	with open(os.path.join(data_dir, "users.json"), 'r') as fp:
		users = json.load(fp)

	with open(os.path.join(data_dir, "mixes.json"), 'r') as fp:
		mixes = json.load(fp)
except:
	print("Database files not found. Run gather.py to get latest data.\n")

# -----------------------------------------------------------------------------
# plot the number of mixes for each of the songs
# -----------------------------------------------------------------------------
num_mixes = []
for song in songs:
	num_mixes.append(len([m for k, m in mixes.items() if m["songId"] == song]))


# create bar plots for all songs
fig, ax = plt.subplots(1, figsize=(20,8))
bp = ax.bar(songs, num_mixes)
plt.xticks(rotation=90)
ax.set_title(f"Number of mixes per song")
ax.set_ylabel("Mixes")
plt.grid(True)
plt.savefig(os.path.join(plot_dir, "mix_count" + plot_type))
plt.close()

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
plt.savefig(os.path.join(plot_dir, "mean_mix_coeff" + plot_type))
plt.close()

# -----------------------------------------------------------------------------
# find the mean mix coefficients for each song by stem type
# -----------------------------------------------------------------------------
# create box plot for stems across all songs
fig, ax = plt.subplots(4, figsize=(20,10))

for idx, stem in enumerate(stems):
	all_mixes = []
	for song in songs:
		all_mixes.append([m[stem] for k, m in mixes.items() if m["songId"] == song and m[stem] > -80])

	bp = ax[idx].boxplot(all_mixes)
	ax[idx].set_xticklabels(songs)
	ax[idx].tick_params(axis='x', rotation=90)
	#ax[idx].set_title(f"{stem} level across all mixes")
	ax[idx].set_ylabel("Gain (dB)")

plt.savefig(os.path.join(plot_dir, "mean_mix_coeff_by_song" + plot_type))
plt.close()

