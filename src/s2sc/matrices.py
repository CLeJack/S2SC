"""
Discrete Customized Fourier Transform

A variation on the idea of the discrete fourier transform

"""
import numpy as np
import waveforms as W

def cmatrix(samples, srate, freqs, phase =0 ):
    """
    A matrix containing complex sinusoids
    at the specified frequencies, sample rate, and samples
    for the discrete customized transform process.

    Consider cmatrix, matrix to be interchangeable terms.
    """

    waves = []

    for f in freqs:
        waves.append(W.complex_sinusoid_s(samples, srate,f, phase))

    return np.array(waves)


def dcft_coeff(cmatrix,signal, **kwargs):
    """
    Get the coefficients associated with the dot product the cmatrix
    and signal

    kwargs for row and ind(ex) can be passed to determine what portion
    of the matrix to run this function on.
    
    This feature is not used in the s2sc project but it could, for example,
    allow matrix multiplication to occur over a subset of frequencies
    or a subset of the target signal which would reduce the computational cost.

    """

    #i = initial, f = final
    rowi = kwargs.get('rowi', 0)
    rowf = kwargs.get('rowf',cmatrix.shape[0])
    indi = kwargs.get('indi', 0)
    indf = kwargs.get('indf', len(signal))

    sig = signal[indi:indf]
    mat = cmatrix[ rowi:rowf, indi:indf]
    output = np.dot(mat, sig)
    return output


def dcft_amplitude(coeff, signal):
    # normalize the coefficients
    return np.abs(coeff) /len(signal)


def dcft(cmatrix,signal, **kwargs):
    """
    the discrete customized transform
    """
    output = dcft_coeff(cmatrix, signal, **kwargs)
    output = dcft_amplitude(output, signal)
    return output


def get_freq(dcft_amplitude, freqs):
    assert(dcft_amplitude.shape == freqs.shape)
    return freqs[np.argmax(dcft_amplitude)]


"""
for reference encase I need something more complicated
than get_freq
I believe the idea for this was to sum all of the energy 
into different peaks
"""
# def dct_concentration(dctamp, octsize = 12):
#     maxind = 0
#     total = 0
#     output =  np.zeros(dctamp.shape)
#     truemax = np.argmax(dctamp) - 2 * octsize

#     for i in range(1, len(dctamp)-1):
#         if (dctamp[i-1] < dctamp[i] and dctamp[i] > dctamp[i+1]) :
#             maxind = i

#         if dctamp[i-1] > dctamp[i] and dctamp[i] < dctamp[i+1] and i >= truemax:
#             output[maxind] = total
#             total = 0
#             maxind = 0
#         else:
#             total += dctamp[i]

#     return output


def get_peaks(arr):
    # naive peak finding for a smooth signal
    # meant to be used specifically with the results of cft.matrix
    output = np.zeros(arr.shape[0])
    for i in range(1,arr.shape[0]-1):
        output[i] = 1 if arr[i-1] < arr[i] > arr[i+1] else 0

    if arr[0] > arr[1]:
        output[0] =1

    end = len(arr) -1
    if arr[end] < arr[end - 1]:
        output[end] = 0

    #this method also assumes a smooth signal
    return output