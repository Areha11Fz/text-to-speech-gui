import PyInstaller.__main__
import customtkinter
import os

# 1. Get the path to the customtkinter library files
ctk_path = os.path.dirname(customtkinter.__file__)

# 2. Define the separator for Windows (;) vs Linux (:)
# Since you are on Windows, we use semicolon
path_separator = ';'

# 3. Arguments for PyInstaller
args = [
    'main.py',                        # Your entry point file
    '--name=TTS_Player_GUI',          # Name of the exe
    '--noconsole',                    # Hide the black command window
    '--onefile',                      # Bundle everything into a single .exe file
    '--clean',                        # Clean cache before building
    
    # This line is crucial: It copies the CustomTkinter theme data to the exe
    f'--add-data={ctk_path}{path_separator}customtkinter',
    
    # Ensure pyttsx3 drivers are included
    '--hidden-import=pyttsx3.drivers',
    '--hidden-import=pyttsx3.drivers.sapi5',
]

# 4. Run the build
print("Building EXE... this might take a minute.")
PyInstaller.__main__.run(args)