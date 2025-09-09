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
        self.values = values[np.argmax(values):].copy() #moving the values away from 0 for convenience
        self.freq = 0
        

        prev = np.roll(self.values, 1)

        starts = ((prev <= 0) & (self.values > 0))
        ends =   ((prev >= 0) & (self.values < 0))

        self.zero_crossing_starts = Audio.get_non_zero_indices(starts)
        self.zero_crossing_ends = Audio.get_non_zero_indices(ends)

        self.start_min = 0
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
    
    def period_samples(self):
        return int(self.srate/max(self.freq,1))

    def set_freq(self, cmat, freqs):
        transform = M.cdft(cmat, self.values)
        self.freq = M.get_freq(transform, freqs)
    
    def start_index_pos(self):
        self.start_index = min(self.start_index + 1, self.zero_crossing_starts.shape[0] - 1) 
        return self.zero_crossing_start()

    def start_index_neg(self):
        self.start_index = max(self.start_index - 1, self.start_min)
        return self.zero_crossing_start()

    def end_index_pos(self):
        self.end_index = min(self.end_index + 1, self.zero_crossing_starts.shape[0] - 1) 
        return self.zero_crossing_end()

    def end_index_neg(self):
        self.end_index = max(self.end_index - 1, self.start_index)
        return self.zero_crossing_end()
    
    def zero_crossing_start(self):
        return self.zero_crossing_starts[self.start_index]
    
    def zero_crossing_end(self):
        """
        zero crossing start occurs when the signal crosses from negative to positive
        and returns the index of the positive value
        taking the sample before that (index - 1) will return the index of
        the negative portion before the zero crossing occurs

        However due to numpy slicing, this -1 offset can be ignored.
        arr[start_index:end_index] will have the last value as the intended target
        """
        return self.zero_crossing_starts[min(self.zero_crossing_starts.shape[0] - 1, self.end_index)]
    
    def find_nearest_period_end(self):

        # subtract current sample index from all possible indices
        # this places the start index at 0 and every index prior at a negative number
        # then subtract the expected period length from all values
        # now the index closes to the target period should be at 0
        reference = self.zero_crossing_starts - self.zero_crossing_start()  - int(self.period_samples())
        
        reference[reference < 0] = 1e9 #seeking minimum error, place a huge error value here
        
        index = np.argmin(reference) # gets the negative portion of the zero crossing prior to actual crossing
        self.end_index = min(index, self.zero_crossing_starts.shape[0] - 1) 
        output = max(self.zero_crossing_end(), self.zero_crossing_start())
        
        print(f"Indices: {self.zero_crossing_start()}, {output} | Expected Samples: {self.period_samples()} | Diff: {output - self.zero_crossing_start()}")
        return output
    
    def create_frame(self, frame_size, peak = 32767):
        start = self.zero_crossing_start()
        end = self.zero_crossing_end()
        final_slice = self.values[start:end]
        print(start, end, final_slice.shape)
        x = np.linspace(0, frame_size, final_slice.shape[0])
        f = interpolate.interp1d(x,final_slice)
        frame = f(np.arange(frame_size))
        frame = peak * frame/np.max(np.abs(frame))
        return frame
    
    def create_wavetable(audio_data, export_path, file_name):
        frames = []        
        
        for a in audio_data:
            
            frames.append(a.create_frame(2048))

        arr = np.concatenate(frames, axis = 0)
        arr = arr.flatten().astype(np.int16)

        p = Path(export_path) / (file_name + '.wav')
        wavfile.write(p,44100, arr)
