import numpy as np
import os
import soundfile as sf
from pathlib import Path
import argparse

def read_wav_file(filepath):
    """Read a WAV file and return its data and sample rate."""
    data, samplerate = sf.read(filepath)
    return data, samplerate

def convert_to_wt_format(wav_data, wave_size):
    """Convert WAV data to WT format."""
    wav_data_float = wav_data.astype(np.float32)
    wave_count = wav_data_float.shape[0] // wave_size

    header = bytearray('vawt', 'utf-8')
    header += wave_size.to_bytes(4, byteorder='little')
    header += wave_count.to_bytes(2, byteorder='little')
    header += (0).to_bytes(2, byteorder='little')

    flattened_data = wav_data_float.flatten()
    wt_data = header + flattened_data.tobytes()
    return wt_data

def save_wt_file(wt_data, output_filepath):
    """Save the WT formatted data to a file."""
    with open(output_filepath, 'wb') as file:
        file.write(wt_data)
