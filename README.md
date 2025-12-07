# TTS Player GUI

A modular, modern Text-to-Speech application for Windows. It allows you to type text and play it back through specific audio hardware (speakers, headphones) or virtual cables (for mixing into microphones).

## 🚀 Features

- **Dual Output:** Option to play audio to your main speakers AND a secondary device (like VB-Cable) simultaneously.
- **Modern UI:** Clean dark-mode interface using `customtkinter`.
- **Hardware Safe:** Auto-detects WASAPI devices and resamples audio frequencies to prevent "Invalid Sample Rate" errors.
- **Window Management:** Automatically centers on your screen upon launch.
- **Modular Code:** Logic, UI, and Entry point are separated for easy maintenance.
- **Build Ready:** Includes a script to compile into a standalone `.exe`.

## 📂 Project Structure

- `main.py`: The entry point script.
- `app_ui.py`: Handles the GUI, buttons, and layout.
- `audio_backend.py`: Handles TTS generation, audio routing, and resampling.
- `build.py`: A script to compile the project into an EXE file.

## 🛠️ Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/YOUR_USERNAME/tts-player-gui.git
    cd tts-player-gui
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **(Optional) Virtual Cable:** To use the secondary output feature for Discord/Games, install [VB-Audio Virtual Cable](https://vb-audio.com/Cable/).

## ▶️ Usage

Run the application via Python:

```bash
python main.py
```

1.  **Select Speaker:** The app auto-selects your default Windows device.
2.  **Dual Output:** Uncheck "Output only to Main Speaker" to reveal the secondary dropdown. This usually auto-selects "CABLE Input".
3.  **Type & Speak:** Type your text and press Enter or click Speak.
4.  **Clear:** Click the "Clear" button to reset the text field.

## 📦 Building the EXE

To create a standalone executable that runs without Python installed:

1.  Ensure you have installed the requirements.
2.  Run the build script:
    ```bash
    python build.py
    ```
3.  Wait for the process to finish.
4.  Navigate to the new `dist` folder.
5.  Your portable **`TTS_Player_GUI.exe`** is ready to use.

## 🔧 Troubleshooting

- **No Audio:** Check if the correct device is selected in the dropdown.
- **EXE crashing immediately:** Ensure you built it using `python build.py` and not just `pyinstaller main.py`, as CustomTkinter needs specific theme files to be copied over.
- **Virus Warning:** If Windows Defender flags the EXE, it is a "False Positive" common with PyInstaller. You may need to add an exception.

## 📄 License

Open Source.
