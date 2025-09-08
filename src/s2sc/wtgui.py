import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import numpy as np
import math


class AudioAnalysisChild:
    """Individual audio analysis component with canvas and controls"""
    
    def __init__(self, parent_frame, index, callback_update_audio=None):
        self.parent_frame = parent_frame
        self.index = index
        self.callback_update_audio = callback_update_audio
        
        # Audio data
        self.audio_data = None
        self.sample_rate = 44100
        self.display_samples = 1000
        self.starting_zero_crossings = 0
        self.ending_zero_crossings = 0
        
        # Index tracking
        self.start_index = 0
        self.end_index = 0
        self.green_line_x = 0
        self.red_line_x = 0
        
        # Create the container frame
        self.container = ttk.Frame(parent_frame, relief='raised', borderwidth=2, padding=10)
        self.container.pack(fill='x', padx=5, pady=5)
        
        # Frequency controls
        freq_frame = ttk.Frame(self.container)
        freq_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(freq_frame, text="Frequency (Hz):").pack(side='left')
        self.freq_var = tk.StringVar(value="440.0")
        self.freq_entry = ttk.Entry(freq_frame, textvariable=self.freq_var, width=10)
        self.freq_entry.pack(side='left', padx=(5, 0))
        
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
        
    def get_frequency(self):
        """Get the current frequency value"""
        try:
            return float(self.freq_var.get())
        except ValueError:
            return 440.0
    
    def set_frequency(self, freq):
        """Set the frequency value"""
        self.freq_var.set(str(freq))
    
    def update_audio_data(self, audio_array, sample_size):
        """Callback function to update audio waveform display"""
        self.audio_data = np.array(audio_array)
        self.display_samples = min(sample_size, len(self.audio_data))
        self.end_index = min(self.display_samples - 1, len(self.audio_data) - 1)
        self.draw_waveform()
    
    def draw_waveform(self):
        """Draw the audio waveform on canvas"""
        self.canvas.delete("all")
        
        if self.audio_data is None or len(self.audio_data) == 0:
            return
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
        
        # Prepare data for display
        # s = (self.sample_rate/self.get_frequency())*4
        display_data = self.audio_data[:self.display_samples]
        # display_data = self.audio_data[:s]
        if len(display_data) == 0:
            return
        
        # Normalize audio data
        if np.max(np.abs(display_data)) > 0:
            normalized_data = display_data / np.max(np.abs(display_data))
        else:
            normalized_data = display_data
        
        # Calculate positions
        x_scale = canvas_width / len(display_data)
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
        self.update_lines()
    
    def update_lines(self):
        """Update the position of start and end lines"""
        canvas_width = self.canvas.winfo_width()
        
        if self.audio_data is None or len(self.audio_data) == 0:
            return
        
        x_scale = canvas_width / self.display_samples
        
        # Green line (start)
        self.green_line_x = self.start_index * x_scale
        self.canvas.create_line(self.green_line_x, 0, self.green_line_x, 
                               self.canvas.winfo_height(), fill='green', width=2)
        
        # Red line (end)
        self.red_line_x = self.end_index * x_scale
        self.canvas.create_line(self.red_line_x, 0, self.red_line_x, 
                               self.canvas.winfo_height(), fill='red', width=2)
    
    def find_zero_crossing(self, index, direction):
        """Find the nearest zero crossing"""
        if self.audio_data is None or len(self.audio_data) == 0:
            return index
        
        current_index = max(0, min(index, len(self.audio_data) - 1))
        
        if direction > 0:  # Moving right
            for i in range(current_index, min(len(self.audio_data) - 1, self.display_samples)):
                if (self.audio_data[i] >= 0 and self.audio_data[i + 1] < 0) or \
                   (self.audio_data[i] < 0 and self.audio_data[i + 1] >= 0):
                    return i
        else:  # Moving left
            for i in range(current_index, 0, -1):
                if (self.audio_data[i] >= 0 and self.audio_data[i - 1] < 0) or \
                   (self.audio_data[i] < 0 and self.audio_data[i - 1] >= 0):
                    return i
        
        return current_index
    
    def move_start_left(self):
        """Move start index to the left (lock to zero crossing)"""
        new_index = self.find_zero_crossing(self.start_index - 1, -1)
        self.start_index = max(0, new_index)
        self.start_label.config(text=str(self.start_index))
        self.draw_waveform()
    
    def move_start_right(self):
        """Move start index to the right (lock to zero crossing)"""
        new_index = self.find_zero_crossing(self.start_index + 1, 1)
        self.start_index = min(self.end_index, new_index)
        self.start_label.config(text=str(self.start_index))
        self.draw_waveform()
    
    def move_end_left(self):
        """Move end index to the left (lock to zero crossing)"""
        new_index = self.find_zero_crossing(self.end_index - 1, -1)
        self.end_index = max(self.start_index, new_index)
        self.end_label.config(text=str(self.end_index))
        self.draw_waveform()
    
    def move_end_right(self):
        """Move end index to the right (lock to zero crossing)"""
        new_index = self.find_zero_crossing(self.end_index + 1, 1)
        self.end_index = min(self.display_samples - 1, new_index)
        self.end_label.config(text=str(self.end_index))
        self.draw_waveform()
    
    def on_canvas_resize(self, event):
        """Handle canvas resize"""
        if self.audio_data is not None:
            self.draw_waveform()
    
    def get_start_index(self):
        """Get current start index"""
        return self.start_index
    
    def get_end_index(self):
        """Get current end index"""
        return self.end_index


class AnalysisWindow:
    """Analysis window with scrollable audio components"""
    
    def __init__(self, parent):
        self.parent = parent
        self.children = []
        
        # Create analysis window
        self.window = tk.Toplevel(parent)
        self.window.title("Audio Analysis")
        self.window.geometry("800x600")
        self.window.transient(parent)
        
        # Center the window
        self.window.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create scrollable frame
        self.create_scrollable_frame(main_frame)
        
        # Create button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Create button
        self.create_button = ttk.Button(button_frame, text="Create", command=self.on_create)
        self.create_button.pack(side='right')
        
        # Add initial child component
        self.add_audio_component()
        self.add_audio_component()
        self.add_audio_component()
        
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
    
    def add_audio_component(self):
        """Add a new audio analysis component"""
        index = len(self.children)
        child = AudioAnalysisChild(self.scrollable_frame, index)
        self.children.append(child)
        
        # Generate sample audio data for demonstration
        sample_rate = 44100
        duration = 0.1  # 0.1 seconds
        t = np.linspace(0, duration, int(sample_rate * duration))
        frequency = 440.0 + (index * 100)  # Different frequency for each component
        audio_data = np.sin(2 * np.pi * frequency * t)
        
        # Add some noise
        audio_data += 0.1 * np.random.randn(len(audio_data))
        
        # Update the component with sample data
        child.update_audio_data(audio_data, len(audio_data))
        child.set_frequency(frequency)
        
        return child
    
    def get_children(self):
        """Get all audio analysis children"""
        return self.children
    
    def on_create(self):
        """Handle create button click - placeholder for model integration"""
        # This function will be overridden by the model portion
        print("Create button clicked - placeholder for model integration")
        print("Analysis data:")
        for i, child in enumerate(self.children):
            print(f"  Component {i}:")
            print(f"    Frequency: {child.get_frequency()}")
            print(f"    Start Index: {child.get_start_index()}")
            print(f"    End Index: {child.get_end_index()}")
        
        messagebox.showinfo("Create", "Analysis complete! (Placeholder function)")
        self.on_close()
    
    def on_close(self):
        """Close the analysis window"""
        self.window.destroy()


class WTGui:
    """Main GUI application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Audio Analysis Tool")
        self.root.geometry("600x400")
        
        # Variables for storing values
        self.output_directory = tk.StringVar(value="../../output/")
        self.filename = tk.StringVar()
        self.input_directory = ""
        
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
        
        # Status label
        self.status_label = ttk.Label(load_frame, text="No directory selected")
        self.status_label.pack(side='left', padx=(10, 0))
    
    def browse_output_directory(self):
        """Browse and select output directory"""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_directory.get()
        )
        if directory:
            self.output_directory.set(directory)
    
    def get_output_directory(self):
        """Get the current output directory"""
        return self.output_directory.get()
    
    def get_filename(self):
        """Get the current filename"""
        return self.filename.get()
    
    def load_files(self):
        """Load files from selected directory and open analysis window"""
        directory = filedialog.askdirectory(title="Select Input Directory")
        if directory:
            self.input_directory = directory
            self.status_label.config(text=f"Selected: {os.path.basename(directory)}")
            
            # Open analysis window
            self.open_analysis_window()
    
    def open_analysis_window(self):
        """Open the analysis window"""
        analysis_window = AnalysisWindow(self.root)
        
        # You can add more audio components here if needed
        # analysis_window.add_audio_component()
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


# Example usage and model integration points
class ModelController:
    """Example model controller to show integration points"""
    
    def __init__(self, gui):
        self.gui = gui
    
    def get_output_directory(self):
        """Get output directory from GUI"""
        return self.gui.get_output_directory()
    
    def get_filename(self):
        """Get filename from GUI"""
        return self.gui.get_filename()
    
    def process_analysis_data(self, analysis_children):
        """Process data from analysis window children"""
        results = []
        for child in analysis_children:
            result = {
                'frequency': child.get_frequency(),
                'start_index': child.get_start_index(),
                'end_index': child.get_end_index()
            }
            results.append(result)
        return results