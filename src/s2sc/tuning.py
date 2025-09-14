import numpy as np

def get_freqs(low_exp, high_exp, ref_freq = 440, semitone = 2**(1/12) ):
    # freq = fundamental * SEMITONE^exponent
    return np.array([ref_freq * semitone ** n for n in range(low_exp, high_exp + 1)])

def get_midi_freqs():
    return get_freqs(-57, 42, 440, 2**(1/12))


def get_note_index(freq, ref_freq=440, semitone=2**(1/12), min_exponent= -57):
    # the lowest note of consideration (i.e. C0_exponent) will be considered 0
    # this can then be used to lookup values from the note table by note name of frequency

    # reverse calculate_notes()
    semitone_to_exp = freq / ref_freq

    return int(.5 + np.log(semitone_to_exp) / np.log(semitone) - min_exponent)

# integer based pitch class
def get_class(index):
    classes = 'C,Cs,D,Ds,E,F,Fs,G,Gs,A,As,B'.split(',')
    return classes[index%12]

def get_octave(index):
    return int(index/12)

def get_class_label(freq, ref_freq=440, semitone=2**(1/12)):
    i = get_note_index(freq, ref_freq= ref_freq, semitone = semitone )
    c = get_class(i)
    o = get_octave(i)
    return c + str(o)


def oct_ind_to_freq(freqs, octave, index):
    i = octave*12 + index
    return freqs[i]