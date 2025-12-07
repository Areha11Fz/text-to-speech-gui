# TTS Player GUI (Dual Output Support)

A modern, modular Python application for Text-to-Speech (TTS) on Windows. It features a clean GUI, audio resampling to prevent hardware errors, and the unique ability to output audio to two devices simultaneously (e.g., your headphones + a virtual microphone for gaming/Discord).

## 🚀 Features

- **Modern GUI:** Built with `customtkinter` for a dark-mode, clean look.
- **Dual Audio Output:** Play TTS to your speakers AND a virtual cable (like VB-Audio) at the same time.
- **Smart Device Filtering:** Automatically filters out duplicate drivers and legacy MME devices, showing only clean WASAPI device names.
- **Auto-Resampling:** Fixes "Invalid Sample Rate" errors by automatically converting TTS audio to match your hardware's Hz (e.g., 48kHz).
- **Global Hotkeys:** (Optional in code) Easy to expand for global keybinds.
- **Modular Code:** Split into logic (`audio_backend.py`), UI (`app_ui.py`), and entry (`main.py`) for easy maintenance.

## 🛠️ Prerequisites

1.  **Python 3.8+** installed on your system.
2.  **(Optional)** [VB-Audio Virtual Cable](https://vb-audio.com/Cable/) if you want to use the "Inject to Mic" feature.

## 📦 Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/YOUR_USERNAME/tts-player-gui.git
    cd tts-player-gui
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ Usage

1.  Run the application:

    ```bash
    python main.py
    ```

2.  **Select Main Speaker:** Choose your headphones/speakers from the top dropdown.
3.  **Dual Output (Optional):**
    - Uncheck **"Output only to Main Speaker"**.
    - A second dropdown will appear.
    - Select your Virtual Cable (e.g., `CABLE Input (VB-Audio Virtual Cable)`).
4.  **Type & Speak:**
    - Type text into the box and press **Enter** or click **Speak**.
    - Use the **Speed** slider to adjust how fast the voice talks.
    - Click **Clear** to reset the text box.

## 📂 Project Structure

- `main.py`: The entry point. Runs the application.
- `app_ui.py`: Handles the Window, Buttons, Checkboxes, and Layouts.
- `audio_backend.py`: Handles the heavy lifting (Generating TTS, finding devices, resampling audio).

## 🔧 Troubleshooting

- **No sound?** Ensure your volume is up and the correct device is selected.
- **Error: "Invalid Sample Rate"?** The app attempts to fix this automatically using `scipy`. If it persists, ensure your device format in Windows Sound Control Panel is set to 44100Hz or 48000Hz.
- **App freezes when speaking?** This app uses threading to prevent freezing, but generating very long text paragraphs may take a moment.

## 📄 License

Open Source. Feel free to modify and use.
