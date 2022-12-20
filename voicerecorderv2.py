import os
import wave
import time
import threading
import pyaudio
import tkinter as tk
import whisper
from gtts import gTTS
from playsound import playsound
from queue import Queue


class VoiceRecorder:
    def __init__(self):
        self.audio_model = whisper.load_model("small")
        self.file_path = "temp.wav"
        self.recordings = Queue()
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.geometry("600x35")
        self.root.attributes("-alpha", 0.9)
        self.root.title("ML Voice Recorder")
        self.button = tk.Button(
            self.root,
            text="🎤",
            command=self.click_handler,
            font=("Arial", 20, "bold"),
        )
        self.button.grid(row=0, column=1)
        self.timestamp = tk.Label(self.root, text="00:00:00", font=("Arial", 20))
        self.timestamp.grid(row=0, column=0)
        self.label = tk.Label(
            self.root,
            text="Press the button to start recording...",
            font=("Arial", 20, "bold"),
        )
        self.label.grid(row=0, column=2)
        self.recording = False
        self.root.mainloop()

    def click_handler(self):
        if self.recording:
            self.recording = False
            self.button.config(text="🎤")
            self.label.config(text="Press the button to start recording...")
            self.recordings = Queue()
        else:
            self.recording = True
            self.button.config(text="🔴")
            threading.Thread(target=self.record).start()
            threading.Thread(target=self.speech_recognition).start()  # self.play_audio

    def record(self):
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,  # best for speech recognition
            rate=44100,  # 16000 is ok though
            input=True,
            frames_per_buffer=1024,  # how often we check for new audio
        )
        frames = []
        start_time = time.time()
        while self.recording:
            data = stream.read(1024)
            frames.append(data)
            passed_time = time.time() - start_time
            secs = int(passed_time % 60)
            mins = int(passed_time / 60 % 60)
            hours = int(passed_time / 3600)
            self.timestamp.config(text=f"{hours:02d}:{mins:02d}:{secs:02d}")
            if (
                len(frames) >= (44100 * 3) / 1024
            ):  # Formula is: rate * seconds_to_record / frames_per_buffer
                self.recordings.put(frames.copy())
                frames = []
        stream.stop_stream()
        stream.close()
        audio.terminate()

    def speech_recognition(self):
        while self.recording:
            frames = self.recordings.get()
            wave_file = wave.open(self.file_path, "wb")
            wave_file.setnchannels(1)
            wave_file.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
            wave_file.setframerate(44100)
            wave_file.writeframes(b"".join(frames))
            wave_file.close()
            result = self.audio_model.transcribe(
                self.file_path, fp16=False, language="english"
            )
            self.label.config(text=result["text"])
            os.remove(self.file_path)

    def play_audio(self):
        while self.recording:
            frames = self.recordings.get()
            wave_file = wave.open(self.file_path, "wb")
            wave_file.setnchannels(1)
            wave_file.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
            wave_file.setframerate(44100)
            wave_file.writeframes(b"".join(frames))
            wave_file.close()
            playsound(self.file_path)
            os.remove(self.file_path)


VoiceRecorder()
