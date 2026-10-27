Set-Location $PSScriptRoot
python -m pip install -r requirements.txt pyinstaller
python -m PyInstaller --noconfirm --onedir --windowed --name PolarHash --icon PolarHash.ico --add-data 'PolarHash.ico;.' --add-data 'PolarHash.png;.' polarhash.py
