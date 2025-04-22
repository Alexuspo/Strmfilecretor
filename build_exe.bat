@echo off
echo Building Jellyfin .strm File Generator executable...
pip install pyinstaller
pyinstaller --onefile --noconsole jellyfin_strm_generator.py
echo.
echo Build complete! The executable can be found in the "dist" folder.
pause