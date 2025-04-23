import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

# Ensure proper path to customtkinter package
try:
    import customtkinter as ctk
except ImportError:
    # If import fails, try to install package automatically
    print("Installing customtkinter library...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
    import customtkinter as ctk

# Basic constants
ACCENT_COLOR = "#3a7ebf"  # main accent color
MODERN_FONT = "Segoe UI"  # modern font for Windows

class JellyfinStrmGenerator:
    def __init__(self, root):
        self.root = root
        
        # Set appearance
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        
        self.root.title("Jellyfin .strm File Generator")
        self.root.geometry("950x650")
        
        # Variables
        self.current_folder = ""
        self.content_type = ""  # "movie" or "series"
        self.season_number = 1  # Default season number
        self.files = []
        self.file_contents = {}
        self.current_file = ""
        self.current_selected_file_btn = None  # To track currently selected file
        self.dialogs = []  # List of active dialogs
        
        # Set application icon
        try:
            if getattr(sys, 'frozen', False):
                application_path = sys._MEIPASS
            else:
                application_path = os.path.dirname(os.path.abspath(__file__))
                
            icon_path = os.path.join(application_path, "icon.ico")
            if (os.path.exists(icon_path)):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # Window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Create UI
        self.setup_ui()
        
        # Initialize
        self.initialize_app()
        
    def on_close(self):
        """Method called when main window is closed"""
        # Close all open dialogs
        for dialog in self.dialogs:
            try:
                dialog.destroy()
            except:
                pass
        self.root.quit()
        self.root.destroy()
        
    def initialize_app(self):
        """Initialize the application"""
        try:
            self.set_status("Select folder to save files...")
            
            # Select initial folder
            folder = self.select_initial_folder()
            if not folder:  # User canceled
                self.root.destroy()
                return
                
            self.current_folder = folder
            # Update displayed folder in UI
            self.folder_label.configure(text=f"Target folder: {self.current_folder}")
            self.set_status("Folder selected, choose content type...")
            
            # Choose content type
            self.show_content_type_dialog()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during application initialization: {str(e)}")
            self.root.destroy()
            
    def setup_ui(self):
        """Create UI components"""
        # Main container with padding
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Top panel with application name
        self.title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.title_frame.pack(fill="x", pady=(0, 20))
        
        # Application title
        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text="Jellyfin .strm File Generator",
            font=(MODERN_FONT, 24, "bold")
        )
        self.title_label.pack(side="left")
        
        # Content type info (top right)
        self.type_badge = ctk.CTkLabel(
            self.title_frame,
            text="⏳ Selecting type...",
            font=(MODERN_FONT, 16),
            fg_color=ACCENT_COLOR,
            corner_radius=8,
            padx=10,
            pady=5,
        )
        self.type_badge.pack(side="right")
        
        # Main layout - split into left and right side
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(fill="both", expand=True)
        
        # Set columns for grid layout
        self.content_frame.grid_columnconfigure(0, weight=1)  # left column
        self.content_frame.grid_columnconfigure(1, weight=3)  # right column (wider)
        self.content_frame.grid_rowconfigure(0, weight=1)  # one row with full height
        
        # --- Left side - file list ---
        self.left_frame = ctk.CTkFrame(self.content_frame)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # File list header
        self.files_header = ctk.CTkLabel(
            self.left_frame,
            text="File list:",
            font=(MODERN_FONT, 16, "bold"),
            anchor="w"
        )
        self.files_header.pack(fill="x", pady=(0, 5))
        
        # File count
        self.file_count = ctk.CTkLabel(
            self.left_frame,
            text=f"Total files: {len(self.files)}",
            font=(MODERN_FONT, 13),
            text_color=("gray60", "gray70"),
            anchor="w"
        )
        self.file_count.pack(fill="x", pady=(0, 10))
        
        # File list with border
        self.filelist_container = ctk.CTkFrame(
            self.left_frame, 
            fg_color=("gray95", "gray20"),
            corner_radius=6
        )
        self.filelist_container.pack(fill="both", expand=True, pady=(0, 10))
        
        # File list - scrollable frame
        self.file_scrollable_frame = ctk.CTkScrollableFrame(
            self.filelist_container, 
            fg_color="transparent"
        )
        self.file_scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Dynamic file buttons will be added in update_file_list
        self.file_buttons = {}
        
        # Buttons for operations
        self.button_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.button_frame.pack(fill="x")
        
        # Grid layout for buttons
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        
        # Reset button
        self.reset_button = ctk.CTkButton(
            self.button_frame,
            text="Start over",
            command=self.reset_app,
            fg_color=("#d1d5db", "#4b5563"),
            font=(MODERN_FONT, 13)
        )
        self.reset_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Change type button
        self.change_type_button = ctk.CTkButton(
            self.button_frame,
            text="Change type",
            command=self.change_content_type,
            fg_color=("#d1d5db", "#4b5563"),
            font=(MODERN_FONT, 13)
        )
        self.change_type_button.grid(row=0, column=1, sticky="ew")
        
        # --- Right side - content editing ---
        self.right_frame = ctk.CTkFrame(self.content_frame)
        self.right_frame.grid(row=0, column=1, sticky="nsew")
        
        # Editor header
        self.editor_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.editor_frame.pack(fill="x", pady=(0, 10))
        
        self.file_icon = ctk.CTkLabel(
            self.editor_frame, 
            text="📄", 
            font=(MODERN_FONT, 20)
        )
        self.file_icon.pack(side="left")
        
        self.file_label = ctk.CTkLabel(
            self.editor_frame,
            text="Editing: ",
            font=(MODERN_FONT, 16, "bold")
        )
        self.file_label.pack(side="left", padx=(5, 0))
        
        # Instructions
        self.url_label = ctk.CTkLabel(
            self.right_frame,
            text="Enter streaming URL address:",
            font=(MODERN_FONT, 14),
            anchor="w"
        )
        self.url_label.pack(fill="x", pady=(0, 5))
        
        # Text field for URL
        self.content_text = ctk.CTkTextbox(
            self.right_frame,
            font=(MODERN_FONT, 13),
            corner_radius=6
        )
        self.content_text.pack(fill="both", expand=True)
        
        # Binding for text changes
        self.content_text.bind("<KeyRelease>", self.save_current_content)
        
        # Help text
        help_text = ("Insert URL for media playback. For example:\n"
                     "http://example.com/stream/video.mp4\n"
                     "or local path: C:\\Videos\\movie.mp4")
        
        self.help_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.help_frame.pack(fill="x", pady=(10, 0))
        
        self.help_icon = ctk.CTkLabel(
            self.help_frame,
            text="💡",
            font=(MODERN_FONT, 16)
        )
        self.help_icon.pack(side="left")
        
        self.help_text = ctk.CTkLabel(
            self.help_frame,
            text=help_text,
            font=(MODERN_FONT, 12),
            text_color=("gray50", "gray70"),
            justify="left"
        )
        self.help_text.pack(side="left", padx=(5, 0))
        
        # Separator
        self.separator = ctk.CTkFrame(
            self.main_frame, 
            fg_color=("gray90", "gray25"),
            height=1
        )
        self.separator.pack(fill="x", pady=15)
        
        # Bottom panel
        self.bottom_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.bottom_frame.pack(fill="x")
        
        # Folder information
        self.folder_info = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.folder_info.pack(side="left")
        
        self.folder_icon = ctk.CTkLabel(
            self.folder_info,
            text="📁",
            font=(MODERN_FONT, 16)
        )
        self.folder_icon.pack(side="left")
        
        self.folder_label = ctk.CTkLabel(
            self.folder_info,
            text="Target folder: Selecting...",
            font=(MODERN_FONT, 13)
        )
        self.folder_label.pack(side="left", padx=(5, 0))
        
        # Change folder button
        self.change_folder_button = ctk.CTkButton(
            self.bottom_frame,
            text="Change folder",
            command=self.change_folder,
            fg_color=("#d1d5db", "#4b5563"),
            font=(MODERN_FONT, 13)
        )
        self.change_folder_button.pack(side="left", padx=(15, 0))
        
        # Generate files button
        self.generate_button = ctk.CTkButton(
            self.bottom_frame,
            text="Generate .strm files",
            command=self.generate_strm_files,
            fg_color=ACCENT_COLOR,
            font=(MODERN_FONT, 13, "bold")
        )
        self.generate_button.pack(side="right")
        
        # Status bar
        self.status_frame = ctk.CTkFrame(self.root)
        self.status_frame.pack(side="bottom", fill="x")
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            anchor="w",
            padx=10,
            pady=3,
            font=(MODERN_FONT, 12)
        )
        self.status_label.pack(fill="x")
    
    def set_status(self, message):
        """Set message in status bar"""
        self.status_label.configure(text=message)
    
    def select_initial_folder(self):
        """Select initial folder - returns selected folder or None"""
        self.root.withdraw()  # Hide main window
        try:
            messagebox.showinfo("Select folder", "Select the folder where you want to save .strm files")
            
            folder = filedialog.askdirectory(title="Select folder for .strm files")
            
            if not folder:  # User canceled
                if messagebox.askretrycancel("No folder selected", "You must select a folder to continue. Try again?"):
                    return self.select_initial_folder()
                else:
                    return None
            
            return folder
        finally:
            self.root.deiconify()  # Show main window
            self.root.update()  # Force UI update
    
    def show_content_type_dialog(self):
        """Show dialog to select content type"""
        dialog = ctk.CTkToplevel(self.root)
        self.dialogs.append(dialog)
        dialog.title("Content type")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Ensure dialog is in foreground
        dialog.lift()
        dialog.focus_force()
        
        # Center dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Variable for selection
        content_type_var = ctk.StringVar(value="movie")
        
        # Title
        title_label = ctk.CTkLabel(
            dialog,
            text="What do you want to add?",
            font=(MODERN_FONT, 22, "bold")
        )
        title_label.pack(pady=(25, 30))
        
        # Container for radio buttons
        options_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        options_frame.pack(fill="x", padx=30)
        
        # Movie
        movie_option = ctk.CTkRadioButton(
            options_frame,
            text="🎬  Movie",
            font=(MODERN_FONT, 16),
            variable=content_type_var,
            value="movie"
        )
        movie_option.pack(anchor="w", pady=5)
        
        # Series
        series_option = ctk.CTkRadioButton(
            options_frame,
            text="📺  Series",
            font=(MODERN_FONT, 16),
            variable=content_type_var,
            value="series"
        )
        series_option.pack(anchor="w", pady=5)
        
        # This function is called when the OK button is clicked
        def on_ok():
            try:
                self.content_type = content_type_var.get()
                dialog.grab_release()
                
                # Update type in UI
                content_type_text = "Movie" if self.content_type == "movie" else "Series"
                content_type_icon = "🎬" if self.content_type == "movie" else "📺"
                self.type_badge.configure(text=f"{content_type_icon} {content_type_text}")
                
                # After closing the dialog, continue based on the selected type
                if dialog in self.dialogs:
                    self.dialogs.remove(dialog)
                dialog.destroy()
                
                # Ensure main window is in foreground
                self.root.after(100, self.root.lift)
                self.root.after(150, self.root.focus_force)
                
                # After closing the dialog, continue based on the selected type
                if self.content_type == "movie":
                    self.setup_movie()
                else:
                    self.show_season_dialog()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while selecting type: {str(e)}")
        
        # OK button
        ok_button = ctk.CTkButton(
            dialog,
            text="Continue",
            font=(MODERN_FONT, 15),
            command=on_ok,
            fg_color=ACCENT_COLOR
        )
        ok_button.pack(pady=25)
        
        # Ensure dialog is properly closed
        def on_dialog_close():
            try:
                dialog.grab_release()
                if dialog in self.dialogs:
                    self.dialogs.remove(dialog)
                dialog.destroy()
                
                # Ensure main window is in foreground
                self.root.after(100, self.root.lift)
                self.root.after(150, self.root.focus_force)
            except:
                pass
            
        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
    
    def show_season_dialog(self):
        """Show dialog to select season number"""
        dialog = ctk.CTkToplevel(self.root)
        self.dialogs.append(dialog)
        dialog.title("Season number")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Ensure dialog is in foreground
        dialog.lift()
        dialog.focus_force()
        
        # Center dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Title
        title_label = ctk.CTkLabel(
            dialog,
            text="Which season is it?",
            font=(MODERN_FONT, 22, "bold")
        )
        title_label.pack(pady=(25, 30))
        
        # Frame for input field with label
        input_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        input_frame.pack(pady=10)
        
        # Label
        season_label = ctk.CTkLabel(
            input_frame,
            text="Season number:",
            font=(MODERN_FONT, 16)
        )
        season_label.pack(side="left", padx=(0, 10))
        
        # Input field with default value
        season_entry = ctk.CTkEntry(
            input_frame,
            width=70,
            font=(MODERN_FONT, 16),
            justify="center"
        )
        season_entry.insert(0, "1")  # Default value
        season_entry.pack(side="left")
        
        # Handle confirmation
        def on_ok():
            try:
                season_str = season_entry.get().strip()
                if not season_str:
                    season = 1
                else:
                    season = int(season_str)
                    if season < 1:
                        season = 1
                
                dialog.grab_release()
                
                # Save season number
                self.season_number = season
                
                # Remove dialog from list and destroy it
                if dialog in self.dialogs:
                    self.dialogs.remove(dialog)
                dialog.destroy()
                
                # Ensure main window is in foreground
                self.root.after(100, self.root.lift)
                self.root.after(150, self.root.focus_force)
                
                # Continue to episode count
                self.show_episode_count_dialog()
            except ValueError:
                messagebox.showerror("Error", "Enter a valid number")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        # OK button
        ok_button = ctk.CTkButton(
            dialog,
            text="Confirm",
            font=(MODERN_FONT, 15),
            command=on_ok,
            fg_color=ACCENT_COLOR
        )
        ok_button.pack(pady=25)
        
        # Ensure dialog is properly closed
        def on_dialog_close():
            try:
                dialog.grab_release()
                if dialog in self.dialogs:
                    self.dialogs.remove(dialog)
                dialog.destroy()
                
                # If user closes dialog with X, use default value
                self.season_number = 1
                
                # Ensure main window is in foreground
                self.root.after(100, self.root.lift)
                self.root.after(150, self.root.focus_force)
                
                # Continue to episode count
                self.show_episode_count_dialog()
            except:
                pass
            
        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
    
    def setup_movie(self):
        """Setup application for movie"""
        self.files = ["movie.strm"]
        self.file_contents = {self.files[0]: ""}
        self.current_file = self.files[0]
        
        # Update UI
        self.update_file_list()
        self.set_status("Movie ready for editing")
        
        # Highlight first file
        self.on_file_select(self.current_file)
    
    def show_episode_count_dialog(self):
        """Show dialog to select episode count"""
        dialog = ctk.CTkToplevel(self.root)
        self.dialogs.append(dialog)
        dialog.title("Episode count")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Ensure dialog is in foreground
        dialog.lift()
        dialog.focus_force()
        
        # Center dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Title
        title_label = ctk.CTkLabel(
            dialog,
            text="How many episodes does the series have?",
            font=(MODERN_FONT, 22, "bold")
        )
        title_label.pack(pady=(25, 30))
        
        # Frame for input field with label
        input_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        input_frame.pack(pady=10)
        
        # Label
        count_label = ctk.CTkLabel(
            input_frame,
            text="Episode count:",
            font=(MODERN_FONT, 16)
        )
        count_label.pack(side="left", padx=(0, 10))
        
        # Input field with default value
        count_entry = ctk.CTkEntry(
            input_frame,
            width=70,
            font=(MODERN_FONT, 16),
            justify="center"
        )
        count_entry.insert(0, "1")  # Default value
        count_entry.pack(side="left")
        
        # Handle confirmation
        def on_ok():
            try:
                count_str = count_entry.get().strip()
                if not count_str:
                    count = 1
                else:
                    count = int(count_str)
                    if count < 1:
                        count = 1
                
                dialog.grab_release()
                
                # Remove dialog from list and destroy it
                if dialog in self.dialogs:
                    self.dialogs.remove(dialog)
                dialog.destroy()
                
                # Ensure main window is in foreground
                self.root.after(100, self.root.lift)
                self.root.after(150, self.root.focus_force)
                
                # Use episode count
                self.setup_series(count)
            except ValueError:
                messagebox.showerror("Error", "Enter a valid number")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        # OK button
        ok_button = ctk.CTkButton(
            dialog,
            text="Confirm",
            font=(MODERN_FONT, 15),
            command=on_ok,
            fg_color=ACCENT_COLOR
        )
        ok_button.pack(pady=25)
        
        # Ensure dialog is properly closed
        def on_dialog_close():
            try:
                dialog.grab_release()
                if dialog in self.dialogs:
                    self.dialogs.remove(dialog)
                dialog.destroy()
                
                # Ensure main window is in foreground
                self.root.after(100, self.root.lift)
                self.root.after(150, self.root.focus_force)
                
                # If user closes dialog with X, create one episode
                self.setup_series(1)
            except:
                pass
            
        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
    
    def setup_series(self, episode_count):
        """Setup application for series"""
        try:
            # Generate file list considering season number
            season_prefix = f"S{self.season_number:02d}"
            self.files = [f"{season_prefix}E{i:02d}.strm" for i in range(1, episode_count + 1)]
            self.file_contents = {file: "" for file in self.files}
            self.current_file = self.files[0] if self.files else ""
            
            # Update UI
            self.update_file_list()
            
            self.set_status(f"Series - season {self.season_number}, {episode_count} episodes ready")
            
            # Highlight first file
            if self.files:
                self.on_file_select(self.files[0])
                
        except Exception as e:
            messagebox.showerror("Error", f"Error setting up series: {str(e)}")
            
    def change_content_type(self):
        """Change content type"""
        if messagebox.askyesno("Change content type", "Changing content type will delete all current files. Continue?"):
            # Reset files
            self.files = []
            self.file_contents = {}
            self.current_file = ""
            self.current_selected_file_btn = None
            
            # Dialog for new type
            self.show_content_type_dialog()
            
            # Reset UI
            self.content_text.delete("1.0", "end")
            self.file_label.configure(text="Editing: ")
            
            self.set_status("Content type changed")
    
    def update_file_list(self):
        """Update file list"""
        # Delete all buttons from list
        for widget in self.file_scrollable_frame.winfo_children():
            widget.destroy()
        self.file_buttons = {}
        
        # Update file count
        self.file_count.configure(text=f"Total files: {len(self.files)}")
        
        # Add buttons for files
        for file in self.files:
            # Lambda function must have local variable to store value for each iteration
            def create_command(f=file):
                return lambda: self.on_file_select(f)
                
            # Create button for file
            btn = ctk.CTkButton(
                self.file_scrollable_frame,
                text=file,
                anchor="w",
                height=35,
                fg_color="transparent", 
                hover_color=("#e0e0e0", "#3a3a3a"),
                text_color=("gray10", "gray90"),
                command=create_command()
            )
            btn.pack(fill="x", pady=(0, 2))
            
            # Save reference to button
            self.file_buttons[file] = btn
            
    def on_file_select(self, selected_file):
        """Handle file selection"""
        try:
            # Save current content
            if self.current_file:
                self.save_current_content()
            
            # Visually highlight selected file
            for file, button in self.file_buttons.items():
                if (file == selected_file):
                    button.configure(fg_color=ACCENT_COLOR, text_color=("white", "white"))
                    self.current_selected_file_btn = button  # Save reference to selected button
                else:
                    button.configure(fg_color="transparent", text_color=("gray10", "gray90"))
            
            # Update current file
            self.current_file = selected_file
            self.file_label.configure(text=f"Editing: {self.current_file}")
            
            # Update content
            self.content_text.delete("1.0", "end")
            self.content_text.insert("1.0", self.file_contents.get(selected_file, ""))
            
            self.set_status(f"Editing: {selected_file}")
        except Exception as e:
            self.set_status(f"Error selecting file: {str(e)}")
    
    def change_folder(self):
        """Change target folder"""
        folder = filedialog.askdirectory(title="Select folder for .strm files")
        if folder:  # User selected folder
            self.current_folder = folder
            self.folder_label.configure(text=f"Target folder: {self.current_folder}")
            self.set_status(f"Folder changed to: {self.current_folder}")
    
    def save_current_content(self, event=None):
        """Save current content to memory"""
        if self.current_file:
            self.file_contents[self.current_file] = self.content_text.get("1.0", "end-1c")
    
    def reset_app(self):
        """Reset application"""
        if messagebox.askyesno("Confirm reset", "This will delete all your current files. Continue?"):
            # Reset files
            self.files = []
            self.file_contents = {}
            self.current_file = ""
            self.current_selected_file_btn = None
            
            # Reset UI
            for widget in self.file_scrollable_frame.winfo_children():
                widget.destroy()
            self.file_buttons = {}
            self.content_text.delete("1.0", "end")
            self.file_label.configure(text="Editing: ")
            self.file_count.configure(text="Total files: 0")
            
            # Dialog for content type
            self.show_content_type_dialog()
            
            self.set_status("Application has been reset")
    
    def generate_strm_files(self):
        """Generate .strm files"""
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
                if not messagebox.askyesno("Warning about empty files", 
                                       f"The following files have no content:\n{empty_file_list}\n\nContinue anyway?"):
                    self.set_status("Generation canceled")
                    return
            
            # Progress bar
            progress_window = ctk.CTkToplevel(self.root)
            self.dialogs.append(progress_window)
            progress_window.title("Generating files")
            progress_window.geometry("400x150")
            progress_window.transient(self.root)
            progress_window.grab_set()
            progress_window.resizable(False, False)
            
            # Ensure dialog is in foreground
            progress_window.lift()
            progress_window.focus_force()
            
            # Center dialog
            progress_window.update_idletasks()
            width = progress_window.winfo_width()
            height = progress_window.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            progress_window.geometry(f"+{x}+{y}")
            
            # Label
            progress_label = ctk.CTkLabel(
                progress_window,
                text="Generating .strm files...",
                font=(MODERN_FONT, 16, "bold")
            )
            progress_label.pack(pady=(20, 15))
            
            # Progress bar
            progress = ctk.CTkProgressBar(
                progress_window,
                width=300,
                height=15,
                corner_radius=5
            )
            progress.pack(pady=10)
            progress.set(0)  # Start at 0
            
            # Status
            status_label = ctk.CTkLabel(
                progress_window,
                text="Preparing...",
                font=(MODERN_FONT, 12)
            )
            status_label.pack(pady=5)
            
            # Generate files
            total_files = len(self.files)
            files_processed = 0
            
            # Update UI
            progress_window.update()
            
            for file_name, content in self.file_contents.items():
                # Update progress bar
                files_processed += 1
                progress_value = files_processed / total_files
                progress.set(progress_value)
                status_label.configure(text=f"Generating: {file_name} ({files_processed}/{total_files})")
                
                # Create file
                file_path = os.path.join(self.current_folder, file_name)
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                
                # Update UI
                progress_window.update()
            
            # After completion
            status_label.configure(text="Completed!")
            
            # Add OK button
            def close_progress():
                if progress_window in self.dialogs:
                    self.dialogs.remove(progress_window)
                progress_window.grab_release()
                progress_window.destroy()
                # Ensure main window is in foreground
                self.root.after(100, self.root.lift)
                self.root.after(150, self.root.focus_force)
            
            ok_button = ctk.CTkButton(
                progress_window,
                text="OK",
                command=close_progress,
                font=(MODERN_FONT, 14),
                width=80
            )
            ok_button.pack(pady=(10, 0))
            
            # Update status
            self.set_status(f"Generated {total_files} files successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving files:\n{str(e)}")
            self.set_status("Error generating files")

# Run application only if file is run directly (not as a module)
if __name__ == "__main__":
    try:
        # Initialize main window and application
        app = ctk.CTk()
        # Ensure application stays in foreground
        app.attributes("-topmost", False)  # Disabled for better user experience
        app.focus_force()
        app.update()
        
        generator = JellyfinStrmGenerator(app)
        
        # Force focus on main window
        app.after(500, app.lift)
        app.after(600, app.focus_force)
        
        # Run main application loop
        app.mainloop()
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        messagebox.showerror("Application Error", f"An unexpected error occurred:\n{str(e)}\n\nDetail:\n{error_detail}")