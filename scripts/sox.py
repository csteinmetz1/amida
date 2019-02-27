import subprocess
import soundfile as sf
import pyloudnorm as pyln

def create_mixdown(stem_paths, output_path):

    # construct appropriate SoX call to mix n track
    call = ""
    for idx, path in enumerate(stem_paths):
        if idx == 0:
            call += """sox "{}" -p | """.format(path)
        elif idx+1 < len(stem_paths):
            call += """sox - -m "{}" -p | """.format(path)
        else:
            call += """sox - -m "{}" "{}" """.format(path, output_path)

    result = subprocess.call(call, shell=True)
    if result:
        raise RuntimeError("Mixdown process failed!")

def loudness_normalize(input_path, output_path, target):

    # measure loudness and determine gain factor to apply
    data, rate = sf.read(input_path)
    meter = pyln.Meter(rate)
    loudness = meter.integrated_loudness(data)
    gain = (target - loudness)

    # construct SoX call to change gain of input track
    call = f"""sox "{input_path}" "{output_path}" gain {gain}"""

    result = subprocess.call(call, shell=True)
    if result:
        raise RuntimeError("Loudness normalization failed!")
    
def trim(input_path, output_path, indices):

    # reformat for SoX - start sample and how many samples to take
    start = indices[0]
    n_samples = indices[1] - indices[0]

    # construct SoX call to trim audio to given samples
    call = f"""sox "{input_path}" "{output_path}" trim {start}s {n_samples}s"""

    result = subprocess.call(call, shell=True)
    if result:
        raise RuntimeError("Trim process failed!")
    

def mono(input_path, output_path):

    call = f"""sox "{input_path}" "{output_path}" remix 1,2"""
    result = subprocess.call(call, shell=True)
    if result:
        raise RuntimeError("Trim process failed!")