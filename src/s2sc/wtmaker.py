import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.io import wavfile
from scipy import interpolate

import tuning as T
import matrices as M

import os
from pathlib import Path
import re


class Audio:

    def __init__(self, srate, values):
        self.srate = srate
        self.values = values
        self.freq = 0
        

        prev = np.roll(self.values, 1)

        starts = ((prev <= 0) & (self.values > 0))
        ends =   ((prev >= 0) & (self.values < 0))

        self.zero_crossing_starts = Audio.get_non_zero_indices(starts)
        self.zero_crossing_ends = Audio.get_non_zero_indices(ends)

        self.start_index = 0
        self.end_index = 0

    @classmethod
    def fromfilename(cls, filename):
        data = wavfile.read(filename)
        srate = data[0]
        values = data[1]
        # data will be normalized internally
        # so attempt a mixdown if there are more than one channels
        if len(values.shape) > 1:
            values = data[1].sum(axis = 1)
        return cls(srate, values)
    
    @classmethod
    def from_arr(cls, srate, arr):
        return cls(srate, arr)
    
    def get_non_zero_indices(indices):
        output = indices * np.arange(indices.shape[0])
        return output[output != 0]
        
    def samples(self):
        return self.values.shape[0]

    def set_freq(self, cmat, freqs):
        transform = M.cdft(cmat, self.values)
        self.freq = M.get_freq(transform, freqs)
    



class SignalData():
    
    def __init__(self, **kwargs):
        self.noteclass =kwargs.get('class','A')
        self.semi = kwargs.get('semi','')
        self.octave = kwargs.get('octave','0')
        self.srate = kwargs.get('srate', 44100)
        self.index = kwargs.get('index', '0')
        self.freq = kwargs.get('freq',27.5)
        self.samples = kwargs.get('samples', 1604)
        self.signal = kwargs.get('signal', pd.DataFrame([],columns=['signal']))
        self.crossings = pd.DataFrame([],columns=['signal'])
        self.frame = kwargs.get('frame', pd.DataFrame([],columns=['signal']))
        self.start_index = 0
        self.end_index = 0
    
    def __str__(self):
        return f'{self.noteclass}, {self.semi}, {self.octave}, {self.index}, {self.freq}, {self.samples}, '\
        f'{self.srate},\n {self.signal}\n {self.frame}\n{self.start_index}, {self.end_index} '


def append_samples(results, data, noteclasses, semi, freqs):
    data.noteclass = results['class']
    data.semi = results['semi']
    data.octave = results['octave']
    data.index =  -5 + noteclasses[data.noteclass] + semi[data.semi] + int(data.octave) * 12
    data.freq = freqs[data.index]
    data.samples = int(np.ceil(data.srate/data.freq))
    return data

def get_signal_data(path):
    s = SignalData()
    signal = wavfile.read(path)
    srate = signal[0]
    df = pd.DataFrame(signal[1].sum(axis = 1) if len(signal[1].shape) > 1 else signal[1], columns = ['signal'])
    s.srate = srate
    s.signal = df
    return s



def create_frame(signal_data, frame_size, peak = 32767):
    start = signal_data.start_index
    end = signal_data.end_index
    final_slice = signal_data.frame['signal'][start:end]
    x = np.linspace(0, frame_size, final_slice.shape[0])
    f = interpolate.interp1d(x,final_slice)
    frame = f(np.arange(frame_size))
    frame = peak * frame/np.max(np.abs(frame))
    return frame

def create_wavetable(signal_data_list, export_path, file_name):
    frames = []        
        
    for s in signal_data_list:
        
        frames.append(create_frame(s, 2048))
    
    arr = np.concatenate(frames, axis = 0)
    arr = arr.flatten().astype(np.int16)
    
    p = Path(export_path) / (file_name + '.wav')
    wavfile.write(p,44100, arr)
    
    
    
    
        
    
def process(root_path):
    # file_data = get_file_data(root_path)
    # frames = [set_frame(f) for f in file_data]
    # file_data.sort(key=lambda x:x.index,reverse = False)
    # return file_data
    pass