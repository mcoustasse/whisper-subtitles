import os  # Used to delete the temporary audio file
import wave  # Used to save the temporary audio file
import time  # Used to get the current time
import threading  # Used to run the recording and speech recognition in parallel threads (so the GUI doesn't freeze)
import pyaudio  # Used to record audio from the microphone
import tkinter as tk  # Used to create the GUI
import whisper  # Used to load the speech recognition model
from gtts import gTTS  # Used to convert text to speech
from playsound import playsound  # Used to play audio files
from queue import Queue  # Used to store recordings


class RealTimeSubtitles:
    def __init__(self):
        """
        Initializes the class.
        """
        # Load the speech recognition model
        self.audio_model = whisper.load_model("small")  # "medium" is the default
        # Set up variables
        self.file_path = "temp.wav"  # Path to the temporary audio file
        self.recordings = Queue()  # Queue of recordings
        self.recording = False  # Whether or not we are recording
        # Set up the GUI
        self.root = tk.Tk()  # Create the window
        self.root.resizable(False, False)  # Make the window not resizable
        self.root.geometry("600x35")  # Set the window size
        self.root.attributes("-alpha", 0.9)  # Set the window transparency
        self.root.title("ML Voice Recorder")  # Set the window title
        self.button = tk.Button(  # Create the button
            self.root,  # Parent widget
            text="🎤",  # Text on the button
            command=self.click_handler,  # Function to call when the button is clicked
            font=("Arial", 20, "bold"),  # Font of the text
        )
        self.button.grid(row=0, column=1)  # Place the button in the window
        self.timestamp = tk.Label(
            self.root, text="00:00:00", font=("Arial", 20)
        )  # Create the timestamp label
        self.timestamp.grid(row=0, column=0)  # Place the timestamp label in the window
        self.label = tk.Label(  # Create the label
            self.root,  # Parent widget
            text="Press the button to start recording...",  # Text on the label
            font=("Arial", 20, "bold"),  # Font of the text
        )
        self.label.grid(row=0, column=2)  # Place the label in the window
        self.root.mainloop()  # Start the GUI

    def click_handler(self):
        """
        Called when the button is clicked.
        """
        if self.recording:  # If we are recording
            self.recording = False  # Stop recording
            self.button.config(text="🎤")  # Change the button text
            self.label.config(
                text="Press the button to start recording..."
            )  # Change the label text
            self.recordings = Queue()  # Clear the queue of recordings
        else:  # If we are not recording
            self.recording = True  # Start recording
            self.button.config(text="🔴")  # Change the button text
            threading.Thread(target=self.record).start()  # Start the recording thread
            threading.Thread(
                target=self.speech_recognition
            ).start()  # Start the speech recognition thread

    def record(self):
        """
        Records audio from the microphone.
        """
        # Set up the microphone
        audio = pyaudio.PyAudio()
        # Start recording
        stream = audio.open(
            format=pyaudio.paInt16,  # 16-bit resolution
            channels=1,  # mono
            rate=44100,  # 44.1kHz sampling rate
            input=True,  # use the microphone as input
            frames_per_buffer=1024,  # number of frames per buffer
        )
        frames = []  # Initialize array to store frames
        start_time = time.time()  # Start the timer
        # Loop until we are done recording
        while self.recording:
            data = stream.read(1024)  # Read 1024 frames from the microphone
            frames.append(data)  # Append the frames to the array
            passed_time = time.time() - start_time  # Calculate the time passed
            secs = int(passed_time % 60)  # Calculate the seconds
            mins = int(passed_time / 60 % 60)  # Calculate the minutes
            hours = int(passed_time / 3600)  # Calculate the hours
            self.timestamp.config(
                text=f"{hours:02d}:{mins:02d}:{secs:02d}"
            )  # Update the timestamp
            # If we have recorded for 3 seconds
            if (
                len(frames) >= (44100 * 3) / 1024
            ):  # Formula is: rate * seconds_to_record / frames_per_buffer
                self.recordings.put(frames.copy())  # Add the frames to the queue
                frames = []  # Clear the frames array
        stream.stop_stream()  # Stop the stream
        stream.close()  # Close the stream
        audio.terminate()  # Terminate the audio object

    def speech_recognition(self):
        """
        Performs speech recognition on the audio.
        """
        # Loop until we are done recording
        while self.recording:
            frames = self.recordings.get()  # Get the frames from the queue
            wave_file = wave.open(self.file_path, "wb")  # Open the temporary audio file
            wave_file.setnchannels(1)  # Set the number of channels
            wave_file.setsampwidth(
                pyaudio.PyAudio().get_sample_size(pyaudio.paInt16)
            )  # Set the sample width
            wave_file.setframerate(44100)  # Set the framerate
            wave_file.writeframes(b"".join(frames))  # Write the frames to the file
            wave_file.close()  # Close the file
            # Perform speech recognition
            result = self.audio_model.transcribe(
                self.file_path,  # Path to the audio file
                fp16=False,  # Whether or not to use 16-bit precision
                language="english",  # Language of the audio
            )
            self.label.config(text=result["text"])  # Update the label text
            os.remove(self.file_path)  # Delete the temporary audio file

    def play_audio(self):
        """
        Plays the audio.
        Note: This is not currently used in the final program.
        """
        # Loop until we are done recording
        while self.recording:
            frames = self.recordings.get()  # Get the frames from the queue
            wave_file = wave.open(self.file_path, "wb")  # Open the temporary audio file
            wave_file.setnchannels(1)  # Set the number of channels
            wave_file.setsampwidth(
                pyaudio.PyAudio().get_sample_size(pyaudio.paInt16)
            )  # Set the sample width
            wave_file.setframerate(44100)  # Set the framerate
            wave_file.writeframes(b"".join(frames))  # Write the frames to the file
            wave_file.close()  # Close the file
            playsound(self.file_path)  # Play the audio
            os.remove(self.file_path)  # Delete the temporary audio file


if __name__ == "__main__":
    RealTimeSubtitles()  # Start the program
