import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import numpy as np
import math
from pathlib import Path
import time

import wtmaker as WT
from functools import reduce

class AudioAnalysisChild:
    """Individual audio analysis component with canvas and controls"""
    
    def __init__(self, parent_frame, index, callback_update_audio=None):
        self.parent_frame = parent_frame
        self.index = index
        self.callback_update_audio = callback_update_audio
        
        # Audio data
        self.display_samples = 0
        
        # Index tracking
        self.green_line_x = 0
        self.red_line_x = 0
        
        # Create the container frame
        self.container = ttk.Frame(parent_frame, relief='raised', borderwidth=2, padding=10)
        self.container.pack(fill='x', padx=5, pady=5)
        
        # Frequency controls
        self.freq_frame = ttk.LabelFrame(self.container, text = "Status")
        self.freq_frame.pack(fill='x', pady=5)
        
        self.status_label = ttk.Label(self.freq_frame, text=self.get_analysis_text(), width = 100)
        self.status_label.pack(side='left', padx=5)
        
        # Canvas for audio waveform
        self.canvas = tk.Canvas(self.container, height=150, bg='white', relief='sunken', borderwidth=1)
        self.canvas.pack(fill='x', pady=5)
        
        # Control buttons frame
        controls_frame = ttk.Frame(self.container)
        controls_frame.pack(fill='x', pady=5)
        
        # Start index controls (green line)
        start_frame = ttk.LabelFrame(controls_frame, text="Start Index (Green)")
        start_frame.pack(side='left', padx=(0, 10))
        
        ttk.Button(start_frame, text="◀", command=self.move_start_left).pack(side='left')
        self.start_label = ttk.Label(start_frame, text="0", width=8)
        self.start_label.pack(side='left', padx=5)
        ttk.Button(start_frame, text="▶", command=self.move_start_right).pack(side='left')
        
        # End index controls (red line)
        end_frame = ttk.LabelFrame(controls_frame, text="End Index (Red)")
        end_frame.pack(side='left')
        
        ttk.Button(end_frame, text="◀", command=self.move_end_left).pack(side='left')
        self.end_label = ttk.Label(end_frame, text="0", width=8)
        self.end_label.pack(side='left', padx=5)
        ttk.Button(end_frame, text="▶", command=self.move_end_right).pack(side='left')
        
        # Bind canvas resize
        self.canvas.bind('<Configure>', self.on_canvas_resize)

    def get_analysis_text(self):
        audio_data = AudioAnalysisGUI.audio_data[self.index]
        expected =  audio_data.period_samples()
        actual = audio_data.zero_crossing_end() - audio_data.zero_crossing_start()
        return f"Frequency (Hz): {audio_data.freq:.2f} | Expected Samples {expected} | Actual Samples: {actual}"
        
    def get_frequency(self):
        """Get the current frequency value"""
        try:
            return float(self.freq_var.get())
        except ValueError:
            return 440.0
    
    def set_frequency(self, freq):
        """Set the frequency value"""
        self.freq_var.set(str(freq))
    
    def update_audio_data(self, sample_size):
        """Callback function to update audio waveform display"""
        self.display_samples = min(sample_size, len(self.audio_data))
        self.draw_waveform()
    
    def draw_waveform(self):
        """Draw the audio waveform on canvas"""
        self.canvas.delete("all")
        audio_data = AudioAnalysisGUI.audio_data[self.index]
        
        if audio_data is None or audio_data.samples() == 0:
            return
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
        
        # Prepare data for display
        self.display_samples = 5 * audio_data.period_samples()
        display_data = audio_data.values[:self.display_samples]
        if display_data.shape[0] == 0:
            return
        
        # Normalize audio data
        if np.max(np.abs(display_data)) > 0:
            normalized_data = display_data / np.max(np.abs(display_data))
        else:
            normalized_data = display_data
        
        # Calculate positions
        x_scale = canvas_width / display_data.shape[0]
        y_center = canvas_height // 2
        y_scale = (canvas_height - 20) // 2
        
        # Draw waveform
        points = []
        for i, sample in enumerate(normalized_data):
            x = i * x_scale
            y = y_center - (sample * y_scale)
            points.extend([x, y])
        
        if len(points) >= 4:
            self.canvas.create_line(points, fill='black', width=1)
        
        # Draw center line
        self.canvas.create_line(0, y_center, canvas_width, y_center, fill='gray', dash=(2, 2))
        
        # Update line positions
        self.update_lines(audio_data)
    
    def update_lines(self, audio_data):
        """Update the position of start and end lines"""
        canvas_width = self.canvas.winfo_width()
        
        x_scale = canvas_width / self.display_samples
        
        # Green line (start)
        ref = audio_data.zero_crossing_start() * x_scale
        
        if self.green_line_x != ref:
            self.green_line_x = ref
            self.canvas.create_line(self.green_line_x, 0, self.green_line_x, 
                                self.canvas.winfo_height(), fill='green', width=2)
            
            # Red line (end)
            self.red_line_x = audio_data.find_nearest_period_end() * x_scale
            self.canvas.create_line(self.red_line_x, 0, self.red_line_x, 
                                self.canvas.winfo_height(), fill='red', width=2)
        else:
            self.green_line_x = audio_data.zero_crossing_start() * x_scale
            self.canvas.create_line(self.green_line_x, 0, self.green_line_x, 
                                self.canvas.winfo_height(), fill='green', width=2)
            
            ref = audio_data.zero_crossing_end() * x_scale

            if self.red_line_x != ref:
                self.red_line_x = ref
                self.canvas.create_line(self.red_line_x, 0, self.red_line_x, 
                                    self.canvas.winfo_height(), fill='red', width=2)
        
        self.start_label.config(text=str(audio_data.zero_crossing_start()))
        self.end_label.config(text=str(audio_data.zero_crossing_end()))
        self.status_label.config(text = str(self.get_analysis_text()))

    
    
    def move_start_left(self):
        """Move start index to the left (lock to zero crossing)"""
        a =  AudioAnalysisGUI.audio_data[self.index]
        # self.start_index = a.start_index_neg()
        a.start_index_neg()
        # self.start_label.config(text=str(a.zero_crossing_start()))
        # self.end_label.config(text=str(a.zero_crossing_end()))
        # self.status_label.config(text = str(self.get_analysis_text()))
        self.draw_waveform()
    
    def move_start_right(self):
        """Move start index to the right (lock to zero crossing)"""
        a =  AudioAnalysisGUI.audio_data[self.index]
        # self.start_index = a.start_index_pos()
        a.start_index_pos()
        # self.start_label.config(text=str(a.zero_crossing_start()))
        # self.end_label.config(text=str(a.zero_crossing_end()))
        # self.status_label.config(text =str(self.get_analysis_text()))
        self.draw_waveform()
    
    def move_end_left(self):
        """Move end index to the left (lock to zero crossing)"""
        a =  AudioAnalysisGUI.audio_data[self.index]
        # self.end_index = a.end_index_neg()
        a.end_index_neg()
        # self.end_label.config(text=str(a.zero_crossing_end()))
        # self.status_label.config(text = str(self.get_analysis_text()))
        self.draw_waveform()
    
    def move_end_right(self):
        """Move end index to the right (lock to zero crossing)"""
        a =  AudioAnalysisGUI.audio_data[self.index]
        # self.end_index = a.end_index_pos()
        a.end_index_pos()
        # self.end_label.config(text=str(a.zero_crossing_end()))
        # self.status_label.config(text =str(self.get_analysis_text()))
        self.draw_waveform()
    
    def on_canvas_resize(self, event):
        """Handle canvas resize"""
        self.draw_waveform()
    
    def get_start_index(self):
        """Get current start index"""
        return self.start_index
    
    def get_end_index(self):
        """Get current end index"""
        return self.end_index


class AnalysisWindow:
    """Analysis window with scrollable audio components"""
    
    def __init__(self,parent_gui, parent, output_directory, filename):
        self.parent_gui = parent_gui
        self.parent = parent
        self.children = []
        
        # Create analysis window
        self.window = tk.Toplevel(parent)
        self.window.title("Audio Analysis")
        self.window.geometry("800x600")
        self.window.transient(parent)

        self.filename = filename
        self.output_directory = output_directory
        
        # Center the window
        self.window.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        analysis_frame = ttk.Frame(main_frame)
        analysis_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create scrollable frame
        self.create_scrollable_frame(analysis_frame)
        
        # Create button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side= "bottom", fill='x', pady=(10, 0))
        
        # Create button
        self.create_button = ttk.Button(button_frame, text="Create", command=self.on_create)
        self.create_button.pack(side='right')
        
        # Add initial child component
        for i, a in enumerate(AudioAnalysisGUI.audio_data):
            self.add_audio_component(i, a)
            self.children[i].draw_waveform()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_scrollable_frame(self, parent):
        """Create a scrollable frame with vertical scrollbar"""
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.canvas.yview)
        
        # Configure canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create frame inside canvas
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Bind events
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Bind mousewheel
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
    
    def on_frame_configure(self, event):
        """Update scroll region when frame size changes"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """Update frame width when canvas size changes"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width)
    
    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def add_audio_component(self, index, audio_data):
        """Add a new audio analysis component with provided data"""
        
        self.children.append(AudioAnalysisChild(self.scrollable_frame, index, audio_data))
    
    def on_create(self):
        """Handle create button click - placeholder for model integration"""
        # This function will be overridden by the model portion
        print("Creating Wavetable")


        print(f"Export State:\n.wav ext: {self.parent_gui.wavext.get()}"
              + f"\n.wt ext: {self.parent_gui.wtext.get()}")

        AudioAnalysisGUI.audio_data.sort(reverse = True) #sort to put longest samples/lowest frequency at the start of wavetable



        WT.Audio.create_wavetable(AudioAnalysisGUI.audio_data, self.output_directory, self.filename)
        WT.Audio.create_wt_wavetable(self.output_directory, self.filename)

        messagebox.showinfo("Create", "Wavetables completed!")
        self.on_close()

    
    def on_close(self):
        """Close the analysis window"""
        self.window.destroy()


class AudioAnalysisGUI:
    """Main GUI application"""
    audio_data = []
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Audio Analysis Tool")
        self.root.geometry("600x500")
        
        # Variables for storing values
        self.output_directory = tk.StringVar(value="../../output/")
        self.filename = tk.StringVar(value="wavetable")
        self.input_directory = ""

        self.cmatrix = []
        self.srate = 48000
        self.samples = 0
        self.freqs = WT.T.get_midi_freqs()

        self.lastdir = ''
        
        self.setup_gui()

        
    
    def setup_gui(self):
        """Setup the main GUI components"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Output directory section
        self.create_output_section(main_frame)
        
        # Filename section
        self.create_filename_section(main_frame)
        
        # Load files button
        self.create_load_files_section(main_frame)

        self.create_checkbox_section(main_frame)

        self.create_status_section(main_frame)

    
    def create_output_section(self, parent):
        """Create output directory selection section"""
        output_frame = ttk.LabelFrame(parent, text="Output Directory", padding="5")
        output_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(output_frame, text="Output:").pack(anchor='w')
        
        dir_frame = ttk.Frame(output_frame)
        dir_frame.pack(fill='x', pady=(5, 0))
        
        self.output_entry = ttk.Entry(dir_frame, textvariable=self.output_directory)
        self.output_entry.pack(side='left', fill='x', expand=True)
        
        ttk.Button(dir_frame, text="Browse", command=self.browse_output_directory).pack(side='right', padx=(5, 0))
    
    def create_filename_section(self, parent):
        """Create filename input section"""
        filename_frame = ttk.LabelFrame(parent, text="Filename", padding="5")
        filename_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(filename_frame, text="Filename:").pack(anchor='w')
        
        self.filename_entry = ttk.Entry(filename_frame, textvariable=self.filename)
        self.filename_entry.pack(fill='x', pady=(5, 0))
    
    def create_load_files_section(self, parent):
        """Create load files button section"""
        load_frame = ttk.Frame(parent)
        load_frame.pack(fill='x', pady=(0, 10))
        
        self.load_button = ttk.Button(load_frame, text="Load Files", command=self.load_files)
        self.load_button.pack(side='left')
        
        # # Status label
        # self.status_label = ttk.Label(load_frame, text="")
        # self.status_label.pack(side='left', padx=(10, 0))
    
    def create_checkbox_section(self,parent):

        checkbox_section = ttk.LabelFrame(parent, text="Exports", padding="5")
        checkbox_section.pack(fill='x', pady=(0, 10))
        
        
        ext_frame = ttk.LabelFrame(checkbox_section, text = "File Type",padding="5")
        ext_frame.pack(side='left', pady=(0, 10))

        self.wavext = tk.BooleanVar()
        self.wavext.set(True)
        self.wtext = tk.BooleanVar()

        self.wavextbox = tk.Checkbutton(ext_frame, text="wav", variable=self.wavext)
        self.wtextbox = tk.Checkbutton(ext_frame, text="wt", variable=self.wtext)

        self.wavextbox.pack(side = 'left')
        self.wtextbox.pack(side = 'left')

    
    def create_status_section(self, parent):
        status_frame = ttk.LabelFrame(parent, text="Status", padding="5")
        status_frame.pack(fill='x', pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(status_frame, text="")
        self.status_label.pack(side='left', padx=(10, 0))
    
    def browse_output_directory(self):
        """Browse and select output directory"""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_directory.get()
        )
        if directory:
            self.output_directory.set(directory)

    
    def create_audio_data(self, files):
        start_time = time.time()
        for i, f in enumerate(files):
            a = WT.Audio.fromfilename(self.input_directory/f)
            # a.set_start_near_max_peak()
            self.audio_data.append(a)
            if(time.time() - start_time > 1):
                self.status_label.config(text=f"Selected: {self.input_directory} \nLoaded {i+ 1} / {len(files)} files")
                self.status_label.update()
                start_time = time.time()
        self.status_label.config(text=f"Selected: {self.input_directory} \nLoaded {i+ 1} / {len(files)} files")
        self.status_label.update()
    

    def delay(self, seconds):
        start_time = time.time()
        while(time.time() - start_time < seconds):
            pass

    def update_frequencies(self):

        common_srates = list(map(lambda x: x.srate, self.audio_data))
        common_srates = list(map(lambda x: x == common_srates[0], common_srates))
        common_srates = reduce(lambda a, b: a == b, common_srates)

        

        if common_srates:
            data = AudioAnalysisGUI.audio_data
            self.samples = max(list(map(lambda x: x.samples(), data)))
            self.srate = data[0].srate

            self.cmatrix = WT.M.cmatrix(self.samples, self.srate, self.freqs)
            start_time = time.time()
            for i, a in enumerate(data):
                a.set_freq(self.cmatrix,self.freqs)
                if(time.time() - start_time > 1):
                    self.status_label.config(text=f"Selected: {self.input_directory} \nAnalyzing file {i + 1} / {len(data)}")
                    self.status_label.update()
                    start_time = time.time()
            self.status_label.config(text=f"Selected: {self.input_directory} \nAnalyzing file {i + 1} / {len(data)}")
            self.status_label.update()
        else:
            self.status_label.config(text=f".wav files had different sample rates.\n Please use file with a common sample rate")

    def load_files(self):
        """Load files from selected directory and open analysis window"""

        if(os.path.exists('lastdir')):
            with open('lastdir', 'r') as f:
                self.lastdir = Path(f.readline())

        directory = filedialog.askdirectory(title="Select Input Directory", initialdir=str(self.lastdir))

        if directory is not None:
            self.input_directory = Path(directory)
            with open('lastdir','w') as f:
                f.write(str(self.input_directory))

            # self.status_label.config(text=f"Selected: {os.path.basename(directory)} Loading ")
            files = os.listdir(directory)
            files = list(filter(lambda x: x.endswith('.wav'), files))

            if len(files) == 0:
                self.status_label.config(text=f"No .wav files found")
            else:
                delay_time = .25
                self.status_label.config(text=f"Selected: {self.input_directory} \nLoading {len(files)} files")
                self.status_label.update()
                self.delay(delay_time)

                self.create_audio_data(files)
                self.delay(delay_time)

                self.update_frequencies()
                self.delay(delay_time)

                self.status_label.config(text=f"Selected: {self.input_directory} \nFile load complete!")
                self.status_label.update()
                self.delay(delay_time)

                self.filename.set(self.lastdir.stem)
                
                self.open_analysis_window()
    
    def open_analysis_window(self):
        """Open the analysis window"""
        analysis_window = AnalysisWindow(self, self.root, self.output_directory.get(), self.filename.get())
        
        # You can add more audio components here if needed
        # analysis_window.add_audio_component()
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()