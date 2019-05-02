import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# useful constants, details, and configuration
# -----------------------------------------------------------------------------
data_dir = "scripts/data"
plot_dir = "plots"
plot_type = ".eps"
stems = ["drums", "bass", "other", "vocals"]
setups = ["headphones", "laptop", "earbuds", "studio", "other"]
songs = np.arange(1, 101)

# -----------------------------------------------------------------------------
# show anon users and mixes done by each (sorted by most mixes)
# -----------------------------------------------------------------------------
def n_mixes_by_user():
    mixes_by_user = sorted([(len(m["mixes"]) if "mixes" in m else 0) for k, m in users.items()], reverse=True)
    user_list = np.arange(1, len(mixes_by_user)+1)

    # create bar plot for all users
    fig, ax = plt.subplots(1, figsize=(8,4))
    bp = ax.bar(user_list, mixes_by_user)
    plt.xticks(user_list, rotation=0)
    ax.set_title(f"Number of mixes by each user")
    ax.set_ylabel("Mixes")
    ax.set_xlabel("Users")
    ax.set_xlim([0, len(mixes_by_user)+1])
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, "n_mixes_by_user" + plot_type))
    plt.close()

# -----------------------------------------------------------------------------
# frequency of different playback methods by number of mixes per setup
# -----------------------------------------------------------------------------
def	n_playback_setups():
    playback_setups = []
    for setup in setups:
        playback_setups.append(np.sum([len(m["mixes"]) for k, m in users.items() if m["playback"] == setup and "mixes" in m]))

    # create bar plot for all users
    fig, ax = plt.subplots(1, figsize=(8,4))
    setups_idx = np.arange(0, len(playback_setups))

    # sort
    sorted_setups = zip(setups, playback_setups)
    sorted_setups = sorted(sorted_setups, key=lambda x: x[1], reverse=True)
    setups_names, counts = zip(*sorted_setups)         
    setups_names = list(setups_names)
    counts = list(counts)

    bp = ax.bar(setups_idx, counts)
    plt.xticks(setups_idx, setups_names)
    ax.set_title(f"Number of mixes performed on each playback setup")
    ax.set_ylabel("Mixes")
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, "n_playback_setups" + plot_type))
    plt.close()

# -----------------------------------------------------------------------------
# plot the number of mixes for each of the songs
# -----------------------------------------------------------------------------
def n_mixes_by_song():
    num_mixes = []
    for song in songs:
        num_mixes.append(len([m for k, m in mixes.items() if m["songId"] == song]))

    # create bar plots for all songs
    fig, ax = plt.subplots(1, figsize=(20,8))
    bp = ax.bar(songs, num_mixes)
    plt.xticks(songs, rotation=90)
    ax.set_title(f"Number of mixes per song")
    ax.set_ylabel("Mixes")
    ax.set_xlim([songs[0]-1,songs[-1]+1])
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, "n_mixes_by_song" + plot_type))
    plt.close()

# -----------------------------------------------------------------------------
# find the mean mix time for each of the songs
# -----------------------------------------------------------------------------
def mean_mix_time_by_song():
    mix_times = []
    for song in songs:
        mix_times.append(np.mean([m['time'] for k, m in mixes.items() if m["songId"] == song]))

    # create bar plots for all songs
    fig, ax = plt.subplots(1, figsize=(20,8))
    bp = ax.bar(songs, mix_times, width=0.8)
    plt.xticks(songs, rotation=90)
    ax.set_title("Mean mix time")
    ax.set_ylabel("Mix time (seconds)")
    ax.set_xlim([songs[0]-1,songs[-1]+1])
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, "mean_mix_time_by_song" + plot_type))
    plt.close()

# -----------------------------------------------------------------------------
# boxplot for the mix time for each song
# -----------------------------------------------------------------------------
def mix_time_by_song():
    all_mixes = []
    for song in songs:
        all_mixes.append([m["time"] for k, m in mixes.items() if m["songId"] == song])

    # create box plot for stems across all songs
    fig, ax = plt.subplots(1, figsize=(20,5))

    bp = ax.boxplot(all_mixes)
    ax.set_xticklabels(songs)
    ax.tick_params(axis='x', rotation=90)
    ax.set_ylabel("Gain (dB)")
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, "mix_time_by_song" + plot_type))
    plt.close()

# -----------------------------------------------------------------------------
# find the mean mix coefficients across all songs
# -----------------------------------------------------------------------------
def mean_mix_coeffs():
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
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, "mean_mix_coeffs" + plot_type))
    plt.close()

# -----------------------------------------------------------------------------
# find the mean mix coefficients for each song by stem type
# -----------------------------------------------------------------------------
def mean_mix_coeff_by_song_stem():
    # create box plot for stems across all songs
    fig, ax = plt.subplots(4, figsize=(20,10))

    for idx, stem in enumerate(stems):
        all_mixes = []
        for song in songs:
            all_mixes.append([m[stem] for k, m in mixes.items() if m["songId"] == song and m[stem] > -80])

        bp = ax[idx].boxplot(all_mixes)
        ax[idx].set_xticklabels(songs)
        ax[idx].tick_params(axis='x', rotation=90)
        ax[idx].text(102, -5, f"{stem}")
        ax[idx].set_ylabel("Gain (dB)")
        ax[idx].set_ylim([-20, 10])


    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, "mean_mix_coeff_by_song_stem" + plot_type))
    plt.close()

# -----------------------------------------------------------------------------
# find the mean mix coefficients for each song by stem type (show only first 10)
# -----------------------------------------------------------------------------
def mean_mix_coeff_by_song_stem_first_n(n):
    # create box plot for stems across all songs
    fig, ax = plt.subplots(4, figsize=(10,10))

    for idx, stem in enumerate(stems):
        all_mixes = []
        for song in songs[0:n]:
            all_mixes.append([m[stem] for k, m in mixes.items() if m["songId"] == song and m[stem] > -80])

        bp = ax[idx].boxplot(all_mixes)
        ax[idx].set_xticklabels(songs)
        ax[idx].tick_params(axis='x', rotation=90)
        ax[idx].text(11, -5, f"{stem}")
        ax[idx].axhline(0, color='grey', linestyle='dotted')
        ax[idx].set_ylabel("Gain (dB)")
        ax[idx].set_ylim([-15, 5])

    plt.savefig(os.path.join(plot_dir, f"mean_mix_coeff_by_song_stem_first_{n}" + plot_type))
    plt.close()

if __name__ == "__main__":

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

    # ------------------------------
    # user analysis
    # ------------------------------
    #n_mixes_by_user()
    #n_mixes_by_song()
    #mean_mix_time_by_song()
    #mix_time_by_song()
    #n_playback_setups()

    # ------------------------------
    # mix analysis
    # ------------------------------
    #mean_mix_coeffs()
    #mean_mix_coeff_by_song_stem()
    mean_mix_coeff_by_song_stem_first_n(10)
