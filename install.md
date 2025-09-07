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


If you've already downloaded the program and have installed all packages, run the following commands to only load the program.

    source ~/Projects/s2scenv/bin/activate
    cd ~/Projects/S2SC/src/s2sc
    python main.py

