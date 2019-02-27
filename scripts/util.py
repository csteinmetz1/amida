import os
import glob
import librosa
import numpy as np
import soundfile as sf
from collections import OrderedDict

def get_songs(path_to_dataset):
    return glob.glob(os.path.join(path_to_dataset, "*"))

def get_stems(path_to_song):
    return glob.glob(os.path.join(path_to_song, "*.wav"))

def find_sample_indices(input_path, length, sample_type):
    """ Measure the integrated gated loudness of a signal.
    
    Params
    -------
    input_path: str
        Path to input audio file.
    length : int
        Sample length in seconds.
    sample_type : str
        One of the following ['highest_energy', 'lowest_energy'].
    Returns
    -------
    indices_data : OrderedDict
        sorted dictionary with rmse values as keys for associated indices
    """

    # load input audio and reshape for librosa
    y, sr = sf.read(input_path)
    y = y.reshape(y.shape[1], y.shape[0])

    # determine the samples in one frame and total frames 
    frame_length = int(sr*length)
    n_frames = int(np.floor(y.shape[1]/frame_length))

    # calculate rmse and find averages over n_frames
    rmse = librosa.feature.rmse(y=y, frame_length=4096)
    rmse = rmse.reshape(rmse.shape[1])
    rmse = rmse[:(rmse.shape[0]-(rmse.shape[0]%n_frames))]
    rmse = np.mean(rmse.reshape(-1, n_frames), axis=0)

    if sample_type == 'highest_energy':
        reverse = True
    else:
        revers = False

    indices_data = OrderedDict({})
    all_indices = [(i*frame_length, (i*frame_length)+frame_length) for i in np.arange(n_frames)]
    for frame, indices in enumerate(all_indices):
        indices_data[rmse[frame]] = indices
    
    # sort indices by descending rmse values (highest first)
    sorted_indices_data = sorted(indices_data.items(), reverse=reverse)
    
    return indices_data

def is_source_active(input_path, indices, rmse_threshold=0.01):

    # load input audio and reshape for librosa
    y, sr = sf.read(input_path, start=indices[0], stop=indices[1])
    y = y.reshape(y.shape[1], y.shape[0])

    rmse = librosa.feature.rmse(y=y, frame_length=4096)
    mean_rmse = np.mean(rmse)

    if mean_rmse > rmse_threshold:
        is_active = True
    else:
        is_active = False

    return is_active