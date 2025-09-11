# S2SC
Convert .wav samples to into single cycle waveforms.

The primary goal of this project is to assist in taking samples of real instruments, and quickly slicing single cycle waveforms from them to generate a wavetable that acts as a decent approximation of the source instrument.

E.g. Samples that contain every note from a classical guitar can be loaded, sliced, and reconstructed into a wave table that creates a guitar like pluck.


## Install Instructions

This project can be installed on a linux platform with the following steps.

1) Create a virtual environment where you would like to install the s2sc project.
    
        mkdir ~/Projects
        cd ~/Projects
        python -m venv s2scenv
    
2) With the above commands, this python environment can be started with:

        source ~/Projects/s2scenv/bin/activate

3) Clone the repo into the same directory.

        git clone https://github.com/CLeJack/S2SC.git

    You should now have the directories
    - ~/Projects/s2scenv
    - ~/Projects/S2SC

4) With the s2scenv still active run:

        cd ~/Projects/S2SC
        pip install -r requirements.txt

5) Switch to source directory then start the program with python:

        cd src/s2sc
        python main.py



6) When finished, close the s2sc virtual environment with:

        deactivate

## Usage

If you've already downloaded the program and have installed all packages, run the following commands to only load the program.

    source ~/Projects/s2scenv/bin/activate
    cd ~/Projects/S2SC/src/s2sc
    python main.py

- .wav and .wt files will be dropped to `~/Projects/S2SC/output` by default with a frame size of 2048. 
  - You may need to separate the .wt and .wav files for import into your daw/vst (this is required for Bitwig wavetable import at the time of this writing)

### Main Window
- **Directory Dialog** box for output directory selection + browse button
- **File name text entry field**
  - defaults to the name of the last directory folder during file load
- **Load files button** - load a series of .wav files either with sample rate of 44100 hz of 48000 hz, then open the analysis.
  - The minimum note is A0 (27.5 hz, 1745 samples at 48kHz) instead of C0 (16.35 hz, 2936 samples at 48kHz) to ensure the waveform can fit into 2048 frames with degradation.
  - Functionality for waveforms with frequencies below A0 is untested.
- **Export** - Export options

### Analysis Window
- **Primary frame** - loads audio data of all of the .wav files from the input directory focused near the highest amplitude in the waveform + a few additional cycles of data.
  - **Status bar** - shows the measured frequency, the expected samples, and the actual samples selected based on your current choice of starting and ending zero crossings.
  - **Start and End buttons** - move to zero crossings which will be used to generated a Single Cycle Waveform
- **Create button** - compiles all of the frames into a wavetable
