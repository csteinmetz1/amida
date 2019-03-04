import os
import sys
import json
import argparse
from tqdm import tqdm

# amida libs
import sox
import util

def process(args):

    # get directories containing stems
    songs = util.get_songs(args.input)  

    print("Processing audio...")
    #for song in tqdm(songs, ncols=80):
    for song in songs:
        song_path = os.path.join(args.output, os.path.basename(song.strip("/")))
        stereo_path = os.path.join(song_path, "stereo")
        mono_path = os.path.join(song_path, "mono")
        if not os.path.isdir(song_path):
            os.makedirs(song_path)     
            os.makedirs(stereo_path)
            os.makedirs(mono_path)

        # create stereo mixdown
        stem_paths = util.get_stems(song)
        mix_output = os.path.join(song_path, "mix.wav")
        sox.create_mixdown(stem_paths, mix_output)

        # get prospective sample from the audio file
        indices_data = util.find_sample_indices(mix_output, 30.0, 'highest_energy')
        os.remove(mix_output) # remove mix (we only need it for analysis)
        
        for rmse, indices in indices_data.items():
            valid_indices = []
            #print("Checking {} with rmse {}".format(indices, rmse))
            # check to ensure all sources are active other this window
            for stem_path in stem_paths:
                active = util.is_source_active(stem_path, indices)
                #print(os.path.basename(stem_path), active)
                valid_indices.append(active)
            if all(valid_indices):
                break

        # check for case where no valid indices were found
        if not all(valid_indices):
            break # skip onto the next song

        for stem_path in stem_paths:
            # operate on the stereo stems
            stereo_output_path = os.path.join(stereo_path, os.path.basename(stem_path))
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
    songs = util.get_songs(args.output)  

    data = []
    for song_path in tqdm(songs, ncols=80):
        song = {}
        song_filename = os.path.basename(song_path.strip("/"))
        song['id'] = int(song_filename.split(' - ')[0])
        song['artist'] = song_filename.split(' - ')[1]
        song['title'] = song_filename.split(' - ')[2]
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

    # create output directory
    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    process(args)

    if args.json:
        database(args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="amida")
    parser.add_argument("input", help="path to input audio stems directory", type=str)
    parser.add_argument("output", help="path to 30 second samples stems directory", type=str)
    parser.add_argument("-j", "--json", help="generate json dataqase file", action="store_true")
    args = parser.parse_args()
    main(args)
