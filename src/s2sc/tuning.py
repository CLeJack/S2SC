import numpy as np



def get_freqs(ref_freq, semitone, low_exp, high_exp):
    # freq = fundamental * SEMITONE^exponent
    return np.array([ref_freq * semitone ** n for n in range(low_exp, high_exp + 1)])


def get_index(freq, refFreq, semitone, minExponent):
    # the lowest note of consideration (i.e. C0_exponent) will be considered 0
    # this can then be used to lookup values from the note table by note name of frequency

    # reverse calculate_notes()
    semitone_to_exp = freq / refFreq

    exponent = np.log(semitone_to_exp) / np.log(semitone)

    # can't go below the lowest exponent / C0
    exponent = max(minExponent, exponent)
    offset = int(0.5 + exponent - minExponent)  # round up to the nearest exponent
    return offset

# integer based pitch class
def get_class_index(freq):

    offset = get_index(freq)
    index = offset % 12
    return index

def get_octave(freq):
    offset = get_index(freq)
    octave = offset//12
    return octave

def oct_ind_to_freq(freqs, octave, index):
    i = octave*12 + index
    return freqs[i]