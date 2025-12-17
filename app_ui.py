import customtkinter as ctk
import threading
import keyboard
from audio_backend import AudioBackend

class TTSApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize Backend
        self.audio = AudioBackend()
        
        # Window Setup
        self.title("TTS Player GUI")
        
        # --- Center Window Logic ---
        window_width = 500
        window_height = 550
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        # ---------------------------

        self.is_speaking = False
        self.placeholder_text = "Type here and press enter..."

        self._setup_ui()

        # --- GLOBAL HOTKEY SETUP ---
        # Speech: Ctrl + Space
        keyboard.add_hotkey('ctrl+space', self.trigger_speech)
        
        # Clear Text: Ctrl + Shift + Space
        keyboard.add_hotkey('ctrl+shift+space', self.trigger_clear_text)

        # Handle app closing safely
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _setup_ui(self):
        """Constructs all GUI elements"""
        dev_names = self.audio.get_device_names()
        default_dev = self.audio.get_default_device_name()

        # 1. Main Speaker
        ctk.CTkLabel(self, text="Main Speaker:").pack(pady=(15, 5))
        self.main_dropdown = ctk.CTkOptionMenu(self, values=dev_names, width=350)
        self.main_dropdown.pack(pady=5)
        
        # Select Default
        if default_dev and default_dev in dev_names:
            self.main_dropdown.set(default_dev)
        
        # 2. Secondary Speaker Checkbox
        self.single_output_var = ctk.BooleanVar(value=False)
        self.chk_single = ctk.CTkCheckBox(self, text="Output only to Main Speaker", 
                                          variable=self.single_output_var, command=self._toggle_secondary)
        self.chk_single.pack(pady=10)

        # 3. Secondary Speaker UI
        self.sec_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkLabel(self.sec_frame, text="Secondary Output:").pack(pady=(5,5))
        self.sec_dropdown = ctk.CTkOptionMenu(self.sec_frame, values=dev_names, width=350)
        self.sec_dropdown.pack(pady=5)

        # 4. Controls
        ctk.CTkLabel(self, text="Speed:").pack(pady=(10, 0))
        self.speed_slider = ctk.CTkSlider(self, from_=50, to=350)
        self.speed_slider.set(200)
        self.speed_slider.pack(pady=5)

        # 5. Text Input
        self.text_entry = ctk.CTkTextbox(self, height=100, width=400, text_color="gray")
        self.text_entry.pack(pady=20)
        self.text_entry.insert("0.0", self.placeholder_text)
        
        self.text_entry.bind("<FocusIn>", self._on_focus_in)
        self.text_entry.bind("<FocusOut>", self._on_focus_out)
        self.text_entry.bind("<Return>", self._on_enter)

        # 6. Buttons Frame
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=5)

        self.speak_btn = ctk.CTkButton(self.btn_frame, text="Speak", command=self.trigger_speech)
        self.speak_btn.pack(side="left", padx=10)

        self.clear_btn = ctk.CTkButton(self.btn_frame, text="Clear", fg_color="#555555", hover_color="#333333", command=self.clear_text)
        self.clear_btn.pack(side="left", padx=10)

        # 7. Status
        self.status_label = ctk.CTkLabel(self, text="Global: Ctrl+Space (Speak) | Ctrl+Shift+Space (Clear)", text_color="gray")
        self.status_label.pack(pady=5)

        self._toggle_secondary()

    def _toggle_secondary(self):
        if self.single_output_var.get():
            self.sec_frame.pack_forget()
        else:
            self.sec_frame.pack(after=self.chk_single, pady=5)
            for name in self.sec_dropdown._values:
                if "CABLE" in name or "VB-Audio" in name:
                    self.sec_dropdown.set(name)
                    break

    def _on_focus_in(self, event):
        if self.text_entry.get("0.0", "end-1c").strip() == self.placeholder_text:
            self.text_entry.delete("0.0", "end")
            self.text_entry.configure(text_color=("black", "white"))

    def _on_focus_out(self, event):
        if not self.text_entry.get("0.0", "end-1c").strip():
            self.text_entry.insert("0.0", self.placeholder_text)
            self.text_entry.configure(text_color="gray")

    def _on_enter(self, event):
        self.trigger_speech()
        return "break"

    def trigger_clear_text(self):
        """Thread-safe wrapper for the global hotkey to clear text"""
        # Global hotkeys run in a background thread. We use .after(0, func)
        # to push the GUI update to the main UI thread to avoid crashes.
        self.after(0, self.clear_text)

    def clear_text(self):
        """Clears text, restores placeholder, and brings window to focus"""
        self.text_entry.delete("0.0", "end")
        self.text_entry.insert("0.0", self.placeholder_text)
        self.text_entry.configure(text_color="gray")
        
        # Bring the window to the front so the user can start typing immediately
        self.deiconify()
        self.focus_force() 
        self.text_entry.focus_set()

    def on_close(self):
        """Clean up hotkeys when closing"""
        try:
            keyboard.unhook_all()
        except:
            pass
        self.destroy()

    def trigger_speech(self):
        if self.is_speaking: 
            return
        threading.Thread(target=self._process_speech_thread, daemon=True).start()

    def _process_speech_thread(self):
        try:
            raw = self.text_entry.get("0.0", "end").strip()
        except RuntimeError:
            return 
            
        text = "Test" if (not raw or raw == self.placeholder_text) else raw

        self.is_speaking = True
        self.speak_btn.configure(state="disabled")
        self.status_label.configure(text="Generating...", text_color="orange")

        try:
            self.audio.generate_tts_file(text, self.speed_slider.get())
            self.status_label.configure(text=f"Playing: '{text}'", text_color="green")
            
            threads = []
            
            t1 = threading.Thread(target=self.audio.play_audio, args=(self.main_dropdown.get(),))
            threads.append(t1)
            t1.start()

            if not self.single_output_var.get():
                sec_name = self.sec_dropdown.get()
                if sec_name != self.main_dropdown.get():
                    t2 = threading.Thread(target=self.audio.play_audio, args=(sec_name,))
                    threads.append(t2)
                    t2.start()

            for t in threads: t.join()
            
            self.status_label.configure(text="Ready (Ctrl+Space)", text_color="gray")

        except Exception as e:
            self.status_label.configure(text=f"Error: {e}", text_color="red")
            print(e)
        finally:
            self.is_speaking = False
            try:
                self.speak_btn.configure(state="normal")
            except:
                pass