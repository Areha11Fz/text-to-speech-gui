import customtkinter as ctk
import pyttsx3
import sounddevice as sd
import soundfile as sf
import os
import tempfile
import threading
import scipy.signal
import numpy as np

try:
    import pythoncom
except ImportError:
    pythoncom = None

class TTSApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TTS Player")
        self.geometry("500x450")
        
        # --- Variables ---
        self.temp_file = os.path.join(tempfile.gettempdir(), "tts_temp_output.wav")
        self.output_devices = self.get_clean_devices()
        self.is_speaking = False
        self.placeholder_text = "Type here and press enter..."
        
        # --- GUI Layout ---
        self.dev_label = ctk.CTkLabel(self, text="Select Speaker:")
        self.dev_label.pack(pady=(15, 5))
        
        dev_names = [d['name'] for d in self.output_devices]
        self.device_dropdown = ctk.CTkOptionMenu(self, values=dev_names, width=350)
        self.device_dropdown.pack(pady=5)
        
        # Auto-Select Default Logic
        default_device_name = self.get_wasapi_default_name()
        if default_device_name and default_device_name in dev_names:
            self.device_dropdown.set(default_device_name)
        elif dev_names:
            self.device_dropdown.set(dev_names[0])

        # Speed Slider
        self.speed_label = ctk.CTkLabel(self, text="Speed:")
        self.speed_label.pack(pady=(10, 0))
        self.speed_slider = ctk.CTkSlider(self, from_=50, to=350)
        self.speed_slider.set(200)
        self.speed_slider.pack(pady=5)
        
        # --- Text Input with Placeholder ---
        self.text_entry = ctk.CTkTextbox(self, height=100, width=400, text_color="gray")
        self.text_entry.pack(pady=20)
        
        # Insert Placeholder initially
        self.text_entry.insert("0.0", self.placeholder_text)
        
        # Bind Focus Events for Placeholder effect
        self.text_entry.bind("<FocusIn>", self.on_focus_in)
        self.text_entry.bind("<FocusOut>", self.on_focus_out)
        self.text_entry.bind("<Return>", self.on_enter_pressed)
        
        # --- Buttons ---
        self.speak_btn = ctk.CTkButton(self, text="Speak", command=self.trigger_speech)
        self.speak_btn.pack(pady=5)

        self.status_label = ctk.CTkLabel(self, text="Ready", text_color="gray")
        self.status_label.pack(pady=5)

    # --- Placeholder Logic ---
    def on_focus_in(self, event):
        """Remove placeholder when user clicks inside"""
        current_text = self.text_entry.get("0.0", "end-1c").strip()
        if current_text == self.placeholder_text:
            self.text_entry.delete("0.0", "end")
            # Change color back to normal (Theme dependent: Black or White)
            self.text_entry.configure(text_color=("black", "white"))

    def on_focus_out(self, event):
        """Restore placeholder if user leaves it empty"""
        current_text = self.text_entry.get("0.0", "end-1c").strip()
        if not current_text:
            self.text_entry.insert("0.0", self.placeholder_text)
            self.text_entry.configure(text_color="gray")

    def get_wasapi_default_name(self):
        try:
            hostapis = sd.query_hostapis()
            for api in hostapis:
                if "WASAPI" in api['name']:
                    def_index = api['default_output_device']
                    if def_index >= 0:
                        return sd.query_devices(def_index)['name']
        except Exception:
            pass
        return None

    def get_clean_devices(self):
        devices = sd.query_devices()
        hostapis = sd.query_hostapis()
        wasapi_index = next((i for i, api in enumerate(hostapis) if "WASAPI" in api['name']), None)
        
        unique = []
        seen = set()
        for i, dev in enumerate(devices):
            if dev['max_output_channels'] > 0:
                if wasapi_index is not None and dev['hostapi'] != wasapi_index:
                    continue
                if dev['name'] not in seen:
                    dev['id'] = i
                    unique.append(dev)
                    seen.add(dev['name'])
        return unique

    def on_enter_pressed(self, event):
        self.trigger_speech()
        return "break"

    def trigger_speech(self):
        if self.is_speaking: return
        threading.Thread(target=self.process_speech, daemon=True).start()

    def process_speech(self):
        # Get text and clean it
        raw_text = self.text_entry.get("0.0", "end").strip()
        
        # LOGIC: If empty or still showing placeholder -> Speak "Test"
        if not raw_text or raw_text == self.placeholder_text:
            text_to_speak = "Test"
        else:
            text_to_speak = raw_text

        self.is_speaking = True
        self.status_label.configure(text="Generating...", text_color="orange")
        self.speak_btn.configure(state="disabled")

        try:
            if pythoncom: pythoncom.CoInitialize()
            
            engine = pyttsx3.init()
            engine.setProperty('rate', int(self.speed_slider.get()))
            engine.save_to_file(text_to_speak, self.temp_file)
            engine.runAndWait()
            del engine

            selected_name = self.device_dropdown.get()
            target_device = next((d for d in self.get_clean_devices() if d['name'] == selected_name), None)
            
            if target_device:
                data, fs = sf.read(self.temp_file)
                target_fs = int(target_device['default_samplerate'])
                
                if fs != target_fs:
                    self.status_label.configure(text="Resampling...", text_color="orange")
                    samples = round(len(data) * float(target_fs) / fs)
                    data = scipy.signal.resample(data, samples)
                    fs = target_fs 

                self.status_label.configure(text=f"Playing: '{text_to_speak}'", text_color="green")
                sd.play(data, fs, device=target_device['id'])
                sd.wait()
            
            self.status_label.configure(text="Ready", text_color="gray")

        except Exception as e:
            self.status_label.configure(text=f"Error: {e}", text_color="red")
            print(f"Error: {e}")
        
        finally:
            self.is_speaking = False
            self.speak_btn.configure(state="normal")
            if pythoncom: pythoncom.CoUninitialize()

if __name__ == "__main__":
    app = TTSApp()
    app.mainloop()