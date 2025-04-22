import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os

class JellyfinStrmGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Jellyfin .strm File Generator")
        self.root.geometry("800x600")
        
        # Set the window icon
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass  # Icon not found, use default
            
        # Variables
        self.current_folder = ""
        self.content_type = ""  # "movie" or "series"
        self.files = []
        self.file_contents = {}
        self.current_file = ""
        
        # Initial folder selection
        self.select_initial_folder()
        
        # Ask for content type
        self.ask_content_type()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create horizontal paned window (splitter)
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left side - file list
        self.left_frame = ttk.Frame(self.paned_window, width=200)
        self.paned_window.add(self.left_frame, weight=1)
        
        # Content type indicator
        self.type_label = ttk.Label(self.left_frame, text=f"Type: {self.content_type.capitalize()}")
        self.type_label.pack(anchor=tk.W, pady=(0, 5))
        
        # File list label
        ttk.Label(self.left_frame, text="Files:").pack(anchor=tk.W, pady=(0, 5))
        
        # File listbox with scrollbar
        self.file_list_frame = ttk.Frame(self.left_frame)
        self.file_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.file_listbox = tk.Listbox(self.file_list_frame)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.file_scrollbar = ttk.Scrollbar(self.file_list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=self.file_scrollbar.set)
        
        # File list bindings
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        
        # Button frame for file operations
        self.file_button_frame = ttk.Frame(self.left_frame)
        self.file_button_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Reset button
        self.reset_button = ttk.Button(self.file_button_frame, text="Start Over", command=self.reset_app)
        self.reset_button.pack(side=tk.LEFT)
        
        # Right side - file content
        self.right_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.right_frame, weight=3)
        
        # Current file label
        self.file_label = ttk.Label(self.right_frame, text="Editing: ")
        self.file_label.pack(anchor=tk.W, pady=(0, 5))
        
        # URL label
        ttk.Label(self.right_frame, text="Enter streaming URL:").pack(anchor=tk.W, pady=(0, 5))
        
        # Text content with scrollbars
        self.content_frame = ttk.Frame(self.right_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        self.content_text = tk.Text(self.content_frame, wrap=tk.WORD)
        self.content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.content_scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=self.content_text.yview)
        self.content_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.content_text.config(yscrollcommand=self.content_scrollbar.set)
        
        # Content binding for auto-save
        self.content_text.bind('<KeyRelease>', self.save_current_content)
        
        # URL help text
        help_text = ("Insert the URL to the media stream. For example:\n"
                    "http://example.com/stream/video.mp4\n"
                    "or a local path like: C:\\\\Videos\\\\movie.mp4")
        ttk.Label(self.right_frame, text=help_text, foreground="gray").pack(anchor=tk.W, pady=(5, 0))
        
        # Bottom frame for save buttons
        self.bottom_frame = ttk.Frame(self.main_frame)
        self.bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Current folder display
        self.folder_label = ttk.Label(self.bottom_frame, text=f"Output folder: {self.current_folder}")
        self.folder_label.pack(side=tk.LEFT)
        
        # Change folder button
        self.change_folder_button = ttk.Button(self.bottom_frame, text="Change Folder", command=self.change_folder)
        self.change_folder_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # Generate button
        self.generate_button = ttk.Button(self.bottom_frame, text="Generate .strm Files", command=self.generate_strm_files)
        self.generate_button.pack(side=tk.RIGHT)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Populate file list based on content type
        self.update_file_list()
        
        # Select first file
        if self.files:
            self.file_listbox.selection_set(0)
            self.on_file_select(None)
        
    def select_initial_folder(self):
        """Prompt user to select initial folder"""
        self.root.withdraw()  # Hide main window during folder selection
        messagebox.showinfo("Folder Selection", "Please select a folder where to create .strm files")
        
        folder = filedialog.askdirectory(title="Select folder for .strm files")
        
        if not folder:  # User cancelled
            if messagebox.askretrycancel("No Folder Selected", "You need to select a folder to continue. Retry?"):
                self.select_initial_folder()
            else:
                self.root.quit()
                return
                
        self.current_folder = folder
        self.root.deiconify()  # Show main window again
    
    def ask_content_type(self):
        """Ask if user is adding a movie or series"""
        content_types = ["Movie", "TV Series"]
        dialog = tk.Toplevel(self.root)
        dialog.title("Content Type")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (self.root.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (self.root.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(dialog, text="What are you adding?", font=("", 12)).pack(pady=(15, 20))
        
        self.content_type_var = tk.StringVar()
        
        for i, ctype in enumerate(content_types):
            rb = ttk.Radiobutton(dialog, text=ctype, variable=self.content_type_var, value=ctype.lower())
            rb.pack(anchor=tk.W, padx=70)
            if i == 0:
                rb.invoke()  # Select the first option by default
        
        def on_ok():
            self.content_type = self.content_type_var.get()
            dialog.destroy()
            if self.content_type == "tv series":
                self.ask_episode_count()
        
        ttk.Button(dialog, text="OK", command=on_ok).pack(pady=(15, 10))
        
        # Make the dialog modal
        self.root.wait_window(dialog)
    
    def ask_episode_count(self):
        """Ask how many episodes the series has"""
        episode_count = simpledialog.askinteger("Episodes", "How many episodes in this series?",
                                                minvalue=1, maxvalue=100)
        
        if episode_count is None or episode_count < 1:  # User cancelled or invalid input
            episode_count = 1  # Default to 1 episode
            
        # Generate file list based on episode count
        self.files = [f"S01E{i:02d}.strm" for i in range(1, episode_count + 1)]
        self.file_contents = {file: "" for file in self.files}
        self.current_file = self.files[0] if self.files else ""
    
    def change_folder(self):
        """Change the output folder"""
        folder = filedialog.askdirectory(title="Select folder for .strm files")
        if folder:  # User selected a folder
            self.current_folder = folder
            self.folder_label.config(text=f"Output folder: {self.current_folder}")
            self.status_var.set(f"Folder changed to: {self.current_folder}")
    
    def update_file_list(self):
        """Update the file list in the UI"""
        # Clear the listbox
        self.file_listbox.delete(0, tk.END)
        
        # If no files yet, create them based on content type
        if not self.files:
            if self.content_type == "movie":
                self.files = ["movie.strm"]
                self.file_contents = {self.files[0]: ""}
                self.current_file = self.files[0]
        
        # Add files to the listbox
        for file in self.files:
            self.file_listbox.insert(tk.END, file)
    
    def on_file_select(self, event):
        """Handle file selection from the list"""
        try:
            # Save current content before switching
            if self.current_file:
                self.save_current_content()
            
            # Get the selected file
            index = self.file_listbox.curselection()[0]
            selected_file = self.file_listbox.get(index)
            
            # Update current file and show content
            self.current_file = selected_file
            self.file_label.config(text=f"Editing: {self.current_file}")
            
            # Clear and insert content
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(tk.END, self.file_contents.get(selected_file, ""))
            
            self.status_var.set(f"Editing: {selected_file}")
        except (IndexError, AttributeError):
            pass  # No selection
    
    def save_current_content(self, event=None):
        """Save the current file content to memory"""
        if self.current_file:
            self.file_contents[self.current_file] = self.content_text.get(1.0, "end-1c")
    
    def reset_app(self):
        """Reset application state and start over"""
        if messagebox.askyesno("Confirm Reset", "This will clear all your work. Continue?"):
            # Clear file data
            self.files = []
            self.file_contents = {}
            self.current_file = ""
            
            # Clear UI
            self.file_listbox.delete(0, tk.END)
            self.content_text.delete(1.0, tk.END)
            self.file_label.config(text="Editing: ")
            
            # Ask for content type again
            self.ask_content_type()
            self.type_label.config(text=f"Type: {self.content_type.capitalize()}")
            
            # Update UI
            self.update_file_list()
            if self.files:
                self.file_listbox.selection_set(0)
                self.on_file_select(None)
            
            self.status_var.set("Reset complete")
    
    def generate_strm_files(self):
        """Generate all .strm files in the selected folder"""
        try:
            # First save current content
            self.save_current_content()
            
            # Check if folder exists
            if not os.path.exists(self.current_folder):
                os.makedirs(self.current_folder)
            
            # Check for empty files
            empty_files = [file for file, content in self.file_contents.items() if not content.strip()]
            if empty_files:
                empty_file_list = "\n".join(empty_files)
                if not messagebox.askyesno("Empty Files Warning", 
                                        f"The following files have no content:\n{empty_file_list}\n\nContinue anyway?"):
                    self.status_var.set("Generation cancelled")
                    return
            
            # Create each file
            for file_name, content in self.file_contents.items():
                file_path = os.path.join(self.current_folder, file_name)
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
            
            messagebox.showinfo("Success", f"Generated {len(self.files)} .strm file(s) in:\n{self.current_folder}")
            self.status_var.set(f"Generated {len(self.files)} file(s) successfully")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving files:\n{str(e)}")
            self.status_var.set("Error generating files")

if __name__ == "__main__":
    root = tk.Tk()
    app = JellyfinStrmGenerator(root)
    root.mainloop()