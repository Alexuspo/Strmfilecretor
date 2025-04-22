import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os

class StrmFileCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("STMR File Creator")
        self.root.geometry("800x600")
        
        # Set the window icon
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass  # Icon not found, use default
            
        # Variables
        self.current_folder = ""
        self.current_file = "untitled.stmr"
        self.files = ["untitled.stmr"]
        self.file_contents = {"untitled.stmr": ""}
        
        # Initial folder selection
        self.select_initial_folder()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create horizontal paned window (splitter)
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left side - file list
        self.left_frame = ttk.Frame(self.paned_window, width=200)
        self.paned_window.add(self.left_frame, weight=1)
        
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
        
        # Populate file list
        self.update_file_list()
        
        # File list bindings
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        
        # Button frame for file operations
        self.file_button_frame = ttk.Frame(self.left_frame)
        self.file_button_frame.pack(fill=tk.X, pady=(5, 0))
        
        # New file button
        self.new_file_button = ttk.Button(self.file_button_frame, text="New File", command=self.new_file)
        self.new_file_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Delete file button
        self.delete_file_button = ttk.Button(self.file_button_frame, text="Delete File", command=self.delete_file)
        self.delete_file_button.pack(side=tk.LEFT)
        
        # Right side - file content
        self.right_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.right_frame, weight=3)
        
        # Current file label
        self.file_label = ttk.Label(self.right_frame, text=f"Editing: {self.current_file}")
        self.file_label.pack(anchor=tk.W, pady=(0, 5))
        
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
        
        # Bottom frame for save buttons
        self.bottom_frame = ttk.Frame(self.main_frame)
        self.bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Current folder display
        self.folder_label = ttk.Label(self.bottom_frame, text=f"Selected folder: {self.current_folder}")
        self.folder_label.pack(side=tk.LEFT)
        
        # Change folder button
        self.change_folder_button = ttk.Button(self.bottom_frame, text="Change Folder", command=self.change_folder)
        self.change_folder_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # Save button
        self.save_button = ttk.Button(self.bottom_frame, text="Generate STMR Files", command=self.generate_stmr_files)
        self.save_button.pack(side=tk.RIGHT)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def select_initial_folder(self):
        """Prompt user to select initial folder"""
        self.root.withdraw()  # Hide main window during folder selection
        messagebox.showinfo("Folder Selection", "Please select a folder where to create .stmr files")
        
        folder = filedialog.askdirectory(title="Select folder for .stmr files")
        
        if not folder:  # User cancelled
            if messagebox.askretrycancel("No Folder Selected", "You need to select a folder to continue. Retry?"):
                self.select_initial_folder()
            else:
                self.root.quit()
                return
                
        self.current_folder = folder
        self.root.deiconify()  # Show main window again
    
    def change_folder(self):
        """Change the output folder"""
        folder = filedialog.askdirectory(title="Select folder for .stmr files")
        if folder:  # User selected a folder
            self.current_folder = folder
            self.folder_label.config(text=f"Selected folder: {self.current_folder}")
            self.status_var.set(f"Folder changed to: {self.current_folder}")
    
    def update_file_list(self):
        """Update the file list in the UI"""
        self.file_listbox.delete(0, tk.END)
        for file in self.files:
            self.file_listbox.insert(tk.END, file)
    
    def on_file_select(self, event):
        """Handle file selection from the list"""
        try:
            # Save current content before switching
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
        self.file_contents[self.current_file] = self.content_text.get(1.0, "end-1c")
    
    def new_file(self):
        """Create a new file"""
        # Ask for file name
        file_name = simpledialog.askstring("New File", "Enter name for the new file:", 
                                           initialvalue="new_file.stmr")
        
        if not file_name:
            return  # User cancelled
            
        # Add .stmr extension if not provided
        if not file_name.lower().endswith('.stmr'):
            file_name += '.stmr'
            
        # Check if file already exists
        if file_name in self.files:
            messagebox.showwarning("Warning", f"File '{file_name}' already exists!")
            return
        
        # Add to files and content
        self.files.append(file_name)
        self.file_contents[file_name] = ""
        
        # Update UI
        self.update_file_list()
        
        # Select the new file
        self.file_listbox.selection_clear(0, tk.END)
        self.file_listbox.selection_set(self.files.index(file_name))
        self.on_file_select(None)  # Force selection change
        
        self.status_var.set(f"Created new file: {file_name}")
    
    def delete_file(self):
        """Delete selected file"""
        try:
            index = self.file_listbox.curselection()[0]
            file_to_delete = self.file_listbox.get(index)
            
            # Don't delete the last file
            if len(self.files) <= 1:
                messagebox.showwarning("Warning", "Cannot delete the last file")
                return
            
            # Confirm deletion
            if messagebox.askyesno("Confirm Delete", f"Delete file '{file_to_delete}'?"):
                # Remove file
                self.files.remove(file_to_delete)
                del self.file_contents[file_to_delete]
                
                # Update UI
                self.update_file_list()
                
                # Select another file
                self.file_listbox.selection_set(0)
                self.on_file_select(None)  # Force selection change
                
                self.status_var.set(f"Deleted file: {file_to_delete}")
        except (IndexError, AttributeError):
            messagebox.showwarning("Warning", "No file selected")
    
    def generate_stmr_files(self):
        """Generate all STMR files in the selected folder"""
        try:
            # First save current content
            self.save_current_content()
            
            # Check if folder exists
            if not os.path.exists(self.current_folder):
                os.makedirs(self.current_folder)
            
            # Create each file
            for file_name, content in self.file_contents.items():
                file_path = os.path.join(self.current_folder, file_name)
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
            
            messagebox.showinfo("Success", f"Generated {len(self.files)} STMR files in:\n{self.current_folder}")
            self.status_var.set(f"Generated {len(self.files)} files successfully")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving files:\n{str(e)}")
            self.status_var.set("Error generating files")

if __name__ == "__main__":
    root = tk.Tk()
    app = StrmFileCreator(root)
    root.mainloop()