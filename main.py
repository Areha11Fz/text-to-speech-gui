import customtkinter as ctk
import pyttsx3
import sounddevice as sd
import soundfile as sf
import keyboard
import os
import tempfile
import threading
import numpy as np

class TTSApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TTS to Mic Injector")
        self.geometry("600x550")
        
        # --- Variables ---
        self.engine = pyttsx3.init()
        self.temp_file = os.path.join(tempfile.gettempdir(), "tts_temp_output.wav")
        self.output_devices = self.get_output_devices()
        
        # --- GUI Layout ---
        
        # 1. Main Speaker (Your Headphones)
        self.lbl_main = ctk.CTkLabel(self, text="Your Speakers (Monitor):")
        self.lbl_main.pack(pady=(10, 0))
        self.main_device_dropdown = ctk.CTkOptionMenu(self, values=[d['name'] for d in self.output_devices], width=400)
        self.main_device_dropdown.pack(pady=5)
        
        # 2. Virtual Mic Output (VB-Cable)
        self.lbl_mic = ctk.CTkLabel(self, text="Virtual Mic (CABLE Input):")
        self.lbl_mic.pack(pady=(10, 0))
        
        # Try to auto-select CABLE Input if it exists
        dev_names = [d['name'] for d in self.output_devices]
        self.mic_device_dropdown = ctk.CTkOptionMenu(self, values=dev_names, width=400)
        self.mic_device_dropdown.pack(pady=5)
        
        # Auto-select VB-Cable if found
        for name in dev_names:
            if "CABLE Input" in name or "VB-Audio" in name:
                self.mic_device_dropdown.set(name)
                break

        # Checkbox to enable/disable mic injection
        self.use_mic_var = ctk.BooleanVar(value=True)
        self.chk_mic = ctk.CTkCheckBox(self, text="Inject to Microphone", variable=self.use_mic_var)
        self.chk_mic.pack(pady=10)

        # 3. Speed
        self.speed_label = ctk.CTkLabel(self, text="Speed:")
        self.speed_label.pack(pady=(10, 0))
        self.speed_slider = ctk.CTkSlider(self, from_=50, to=400)
        self.speed_slider.set(200)
        self.speed_slider.pack(pady=5)
        
        # 4. Text Input
        self.text_entry = ctk.CTkTextbox(self, height=100, width=500)
        self.text_entry.pack(pady=20)
        self.text_entry.insert("0.0", "Hello world")
        
        # 5. Buttons
        self.speak_btn = ctk.CTkButton(self, text="Speak (Enter)", command=self.trigger_speech)
        self.speak_btn.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="Ready", text_color="gray")
        self.status_label.pack(pady=5)

        # --- Bindings ---
        self.text_entry.bind("<Return>", self.on_enter_pressed)
        keyboard.add_hotkey('F8', self.trigger_speech)

    def get_output_devices(self):
        """Get list of output devices"""
        devices = sd.query_devices()
        outputs = []
        for i, dev in enumerate(devices):
            if dev['max_output_channels'] > 0:
                dev['id'] = i 
                outputs.append(dev)
        return outputs

    def on_enter_pressed(self, event):
        self.trigger_speech()
        return "break"

    def trigger_speech(self):
        threading.Thread(target=self.process_speech, daemon=True).start()

    def play_audio(self, data, fs, device_name):
        """Helper to play audio on a specific device"""
        try:
            device_id = next(d['id'] for d in self.output_devices if d['name'] == device_name)
            sd.play(data, fs, device=device_id)
            sd.wait()
        except Exception as e:
            print(f"Error playing on {device_name}: {e}")

    def process_speech(self):
        text = self.text_entry.get("0.0", "end").strip()
        if not text: return

        self.status_label.configure(text="Generating...", text_color="orange")
        
        try:
            # Generate Audio
            rate = int(self.speed_slider.get())
            self.engine.setProperty('rate', rate)
            self.engine.save_to_file(text, self.temp_file)
            self.engine.runAndWait()
            
            # Read Audio
            data, fs = sf.read(self.temp_file)
            
            # Identify devices
            main_speaker = self.main_device_dropdown.get()
            mic_injector = self.mic_device_dropdown.get()
            
            threads = []
            
            # 1. Thread for Main Speaker (Monitoring)
            t1 = threading.Thread(target=self.play_audio, args=(data, fs, main_speaker))
            threads.append(t1)
            t1.start()
            
            # 2. Thread for Virtual Mic (Injection)
            if self.use_mic_var.get():
                t2 = threading.Thread(target=self.play_audio, args=(data, fs, mic_injector))
                threads.append(t2)
                t2.start()

            self.status_label.configure(text="Speaking...", text_color="green")
            
            # Wait for threads to finish
            for t in threads:
                t.join()
                
            self.status_label.configure(text="Ready", text_color="gray")
            
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}", text_color="red")
            print(e)

if __name__ == "__main__":
    app = TTSApp()
    app.mainloop()