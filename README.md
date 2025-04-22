# STMR File Creator

A simple application for creating and managing `.stmr` files.

## How to Use

1. **Starting the Application**:
   - Run `stmr_file_creator.py` by double-clicking it or using Python: `python stmr_file_creator.py`
   - On first run, you'll be asked to select a folder where your .stmr files will be saved

2. **Interface**:
   - **Left Side**: List of .stmr files you're working with
   - **Right Side**: Content editor for the selected file
   - **Bottom**: Shows the current output folder and buttons for changing folder and generating files

3. **Working with Files**:
   - **Create a New File**: Click the "New File" button and enter a name
   - **Delete a File**: Select a file and click the "Delete File" button
   - **Edit a File**: Select a file from the list and edit its content in the right panel

4. **Generating Files**:
   - Click "Generate STMR Files" at the bottom right to save all files to your selected folder

## Requirements

- Python 3.x
- Tkinter (usually included with Python)

## Notes

- Files are automatically saved in memory when you switch between them
- The application starts with a default "untitled.stmr" file