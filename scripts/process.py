import os
import sys
import json
import argparse
from tqdm import tqdm

# amida libs
import sox
import util

def process(args):

    # sample rate of input audio
    fs = 44100

    # get prospective sample from the audio file
    songs = json.load(open("songs.json"))

    print("Processing audio...")
    for song in songs:
    #for song in tqdm(songs, ncols=80):
        song_path = os.path.join(args.output, os.path.split(os.path.normpath(song['path']))[-1])
        stereo_path = os.path.join(song_path, "stereo")
        mono_path = os.path.join(song_path, "mono")
        if not os.path.isdir(song_path):
            os.makedirs(song_path)     
            os.makedirs(stereo_path)
            os.makedirs(mono_path)

        # iterate over stems for each song
        for stem_path in util.get_stems(os.path.join(song['path'])):
            # operate on the stereo stems
            stereo_output_path = os.path.join(stereo_path, os.path.basename(stem_path))
            indices = (song['start'] * fs, song['stop'] * fs)
            sox.trim(stem_path, stereo_output_path, indices)
            sox.loudness_normalize(stereo_output_path, 
                                   stereo_output_path.replace(".wav", "_out.wav"), 
                                   -28.0)
            # remove source file and rename normalized to orignal
            os.remove(stereo_output_path)
            os.rename(stereo_output_path.replace(".wav", "_out.wav"), stereo_output_path)

            # operate on the mono stems (and create them)
            mono_output_path = os.path.join(mono_path, os.path.basename(stem_path))
            sox.mono(stem_path, mono_output_path)
            sox.trim(mono_output_path, 
                     mono_output_path.replace(".wav", "_out.wav"), 
                     indices)
            sox.loudness_normalize(mono_output_path.replace(".wav", "_out.wav"), 
                                   mono_output_path.replace(".wav", "_out2.wav"), -28.0)

            # remove source files and rename normalized to orignal
            os.remove(mono_output_path)
            os.remove(mono_output_path.replace(".wav", "_out.wav"))
            os.rename(mono_output_path.replace(".wav", "_out2.wav"), mono_output_path)

def database(args):

    # get directories containing stems
    songs = json.load(open("songs.json"))

    data = []
    for song in tqdm(songs, ncols=80):
        song_path = os.path.join(args.output, 
                    os.path.split(os.path.normpath(song['path']))[-1])

        # add paths
        song['tracks'] = {
            'mono'   : {},
            'stereo' : {}
        }

        mono_path = os.path.join(song_path, "mono")
        stereo_path = os.path.join(song_path, "stereo")

        for stem in util.get_stems(mono_path):
            stem_type = os.path.basename(stem).replace('.wav', '')
            song['tracks']['mono'][stem_type] = stem

        for stem in util.get_stems(stereo_path):
            stem_type = os.path.basename(stem).replace('.wav', '')
            song['tracks']['stereo'][stem_type] = stem

        data.append(song)

    with open(os.path.join(args.output, 'data.json'), 'w') as outfile:  
        json.dump(data, outfile)

def main(args):

    if args.song_idx:
        util.generate_song_idx_json(args.input, "songs.json")
        return None

    # create output directory
    if not os.path.isdir(args.output):
        print(args.output)
        os.makedirs(args.output)

    process(args)

    if args.json:
        database(args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="amida")
    parser.add_argument("input", help="path to input audio stems directory", type=str)
    parser.add_argument("output", help="path to 30 second samples stems directory", type=str)
    parser.add_argument("-j", "--json", help="generate json dataqase file", action="store_true")
    parser.add_argument("-s", "--song_idx", help="generate boilerplate indices json file", action="store_true")
    args = parser.parse_args()
    main(args)
