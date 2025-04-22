@echo off
echo Building STMR File Creator executable...
pip install pyinstaller
pyinstaller --onefile --noconsole stmr_file_creator.py
echo.
echo Build complete! The executable can be found in the "dist" folder.
pause