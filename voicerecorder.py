import os
import wave
import time
import threading
import pyaudio
import tkinter as tk
from PIL import Image, ImageTk
import whisper
from gtts import gTTS
from playsound import playsound


class VoiceRecorder:
    def __init__(self):
        self.audio_model = whisper.load_model("medium")
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.title("ML Voice Recorder")
        self.black_mic_image = Image.open("black_mic.jpg")
        self.red_mic_image = Image.open("red_mic.jpg")
        self.black_mic = self.imageProcessing(self.black_mic_image)
        self.red_mic = self.imageProcessing(self.red_mic_image)
        self.button = tk.Button(
            self.root,
            image=self.black_mic,
            command=self.click_handler,
        )
        self.button.pack()
        self.label = tk.Label(self.root, text="00:00:00", font=("Arial", 12))
        self.label.pack()
        self.recording = False
        self.root.mainloop()

    def imageProcessing(self, image: Image, width: int = 150, height: int = 150):
        result = image.resize((width, height))
        return ImageTk.PhotoImage(result)

    def click_handler(self):
        if self.recording:
            self.recording = False
            self.button.config(image=self.black_mic)
        else:
            self.recording = True
            self.button.config(image=self.red_mic)
            threading.Thread(target=self.record).start()

    def record(self):
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,  # best for speech recognition
            rate=44100,  # 16000 is ok
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
            self.label.config(text=f"{hours:02d}:{mins:02d}:{secs:02d}")
        stream.stop_stream()
        stream.close()
        audio.terminate()

        exists = True
        i = 1
        while exists:
            if os.path.exists(f"output{i}.wav"):
                i += 1
            else:
                exists = False
        waveFile = wave.open(f"output{i}.wav", "wb")
        waveFile.setnchannels(1)
        waveFile.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        waveFile.setframerate(44100)
        waveFile.writeframes(b"".join(frames))
        waveFile.close()
        # self.whisper_transcribe(f"output{i}.wav")
        translation = self.whisper_translate(f"output{i}.wav")
        audio = gTTS(text=translation, lang="en", slow=False)
        audio.save("example.mp3")
        playsound(
            "/Users/mcoustasse/Matias/Coding/Github/whisper-subtitles/example.mp3"
        )

    def whisper_transcribe(self, file_path: str):
        result = self.audio_model.transcribe(file_path, language="spanish")
        print(result["text"])
        return result["text"]

    def whisper_translate(self, file_path: str):
        result = self.audio_model.transcribe(
            file_path, task="translate", language="spanish"
        )
        print(result["text"])
        return result["text"]


VoiceRecorder()
