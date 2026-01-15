import pyttsx3
import sounddevice as sd
import soundfile as sf
import scipy.signal
import numpy as np
import os
import tempfile

try:
    import pythoncom
except ImportError:
    pythoncom = None


class AudioBackend:
    def __init__(self):
        self.temp_file = os.path.join(
            tempfile.gettempdir(), "tts_temp_output.wav")
        self.devices = self._scan_devices()
        self.voices = self._scan_voices()  # <--- NEW: Load voices on startup

    def _scan_devices(self):
        """Internal: Scans and filters for WASAPI output devices."""
        devices = sd.query_devices()
        hostapis = sd.query_hostapis()

        wasapi_index = next((i for i, api in enumerate(
            hostapis) if "WASAPI" in api['name']), None)

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

    def _scan_voices(self):
        """Internal: Scans for available system voices"""
        if pythoncom:
            pythoncom.CoInitialize()
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        # Store as a dictionary { "Voice Name": "Voice ID" }
        voice_dict = {}
        for v in voices:
            # Clean up name (remove long path junk if present)
            name = v.name.replace("Microsoft ", "").replace(" Desktop", "")
            voice_dict[name] = v.id
        del engine
        if pythoncom:
            pythoncom.CoUninitialize()
        return voice_dict

    def get_device_names(self):
        return [d['name'] for d in self.devices]

    def get_voice_names(self):
        """Returns list of human-readable voice names"""
        return list(self.voices.keys())

    def get_default_device_name(self):
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

    def generate_tts_file(self, text, speed, voice_name=None):
        """Generates WAV file with specific speed AND voice"""
        if pythoncom:
            pythoncom.CoInitialize()

        engine = pyttsx3.init()
        engine.setProperty('rate', int(speed))

        # <--- NEW: Set the specific voice ID
        if voice_name and voice_name in self.voices:
            engine.setProperty('voice', self.voices[voice_name])

        engine.save_to_file(text, self.temp_file)
        engine.runAndWait()
        del engine

        if pythoncom:
            pythoncom.CoUninitialize()
        return self.temp_file

    def play_audio(self, device_name):
        target_device = next(
            (d for d in self.devices if d['name'] == device_name), None)

        if not target_device:
            print(f"Device not found: {device_name}")
            return

        try:
            data, fs = sf.read(self.temp_file)
            target_fs = int(target_device['default_samplerate'])

            if fs != target_fs:
                number_of_samples = round(len(data) * float(target_fs) / fs)
                data = scipy.signal.resample(data, number_of_samples)
                fs = target_fs

            sd.play(data, fs, device=target_device['id'])
            sd.wait()
        except Exception as e:
            print(f"Error playing on {device_name}: {e}")
