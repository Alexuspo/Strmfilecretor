@echo off
echo Instaluji potrebne knihovny...
pip install pyinstaller customtkinter ttkthemes

echo.
echo Sestavuji Jellyfin .strm File Generator...
pyinstaller --onefile --noconsole --name "Jellyfin.strm.Generator" jellyfin_strm_generator.py
echo.
echo Sestaveni dokonceno! Spustitelny soubor najdete ve slozce "dist".
pause