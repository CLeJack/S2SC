import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import wtgui


if __name__ == "__main__":
    # Create and run the application
    app = wtgui.AudioAnalysisGUI()

    # Example of model integration
    # model = ModelController(app)
    
    app.run()

"""
I would like a tkinter gui with the following components and functionality

output text box 
- label that says output 
- auto populate text box with default output directory ../../output/
- browse button to set the output and select a directory
- store the directory or default value as a variable to be referenced by the model portion of the program

filename textbox
- label that says filename
- function that gets the text value in this box for the model portion of the controller

load files button
- give a file navigation menu that expects a directory for the input



Analysis Window
- create a new window with a centered container that has a vertical scroll bar
  - this container will hold multiple child containers each with a canvas to draw audio data on
   - the child components should be accessible by the model to get data elements listed below
   - a text box that shows a value for a frequency but can also be adjusted to put an automated frequency with a handle to reference the value later
   - a call back function that takes an array values that represent an audio waveform, and a sample size value to show how much of the signal to display
   - left and right button controls for a green vertical line on the window to show the starting index where the audio data will be split which locks to zero crossings
   - another pair of left and right button controls for a red vertical line that show the ending index where the audio data will be split which locks to zero crossings
    - variables that track both the starting and ending index will be needed for the model portion of the controller later
 - create button
    that will hold a place holder function that will be handled by the model portion of the code.
    after this is done the analysis window should close allowing the user to go to another set of files






"""