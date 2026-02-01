import threading 
import sys 
import time 
import pyaudio 
import numpy as np
import matplotlib.pyplot as plt
import wave 
import speech_recognition as sr 
from speech_recognition import AudioData

stop_event = threading.Event()

def wait_for_enter():
    input("Press Enter to stop recording...\n")
    stop_event.set()

def spinner():
    """Displays a visual spinner while recording."""
    chars = '|/-\\'
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f'\rRecording... {chars[i % 4]}')
        sys.stdout.flush()
        i += 1
        time.sleep(0.1)
    print("\rRecording complete!            ")

def record_audio():
    """Records voice from the microphone until Enter is pressed."""
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    frames = []
    
    threading.Thread(target=wait_for_enter, daemon=True).start()
    threading.Thread(target=spinner, daemon=True).start()
    
    while not stop_event.is_set():
        frames.append(stream.read(1024))    
    
    stream.stop_stream()
    stream.close()
    width = p.get_sample_size(pyaudio.paInt16)
    p.terminate()
    return b''.join(frames), 16000, width

def save_audio(data, rate, width, filename="my_audio.wav"):
    """Saves the recorded audio as a .wav file."""
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(width)
        wf.setframerate(rate)
        wf.writeframes(data)
    print(f"Audio saved to: {filename}")

def transcribe_and_save(data, rate, width):
    """Transcribes audio using Google API and saves text to .txt."""
    recognizer = sr.Recognizer()
    audio = AudioData(data, rate, width)
    
    try:
        text = recognizer.recognize_google(audio)
        print(f"Transcription: {text}")
        
        with open("my_transcript.txt", "w") as f:
            f.write(text)
        print("Transcription saved to: my_transcript.txt")
        
    except sr.UnknownValueError:
        print("Error: AI could not understand the audio.")
    except sr.RequestError as e:
        print(f"API Error: {e}")

def plot_waveform(data, rate):
    """Displays the digital waveform using Matplotlib."""
    samples = np.frombuffer(data, dtype=np.int16)
    time_axis = np.linspace(0, len(samples)/rate, len(samples))
    
    plt.figure(figsize=(10, 4))
    plt.plot(time_axis, samples, color='blue')
    plt.title("Voice Waveform Visualization")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")
    plt.grid(True, alpha=0.3)
    plt.show()

def main():
    print("="*40)
    print("MY VOICE, MY WORDS: VOICE-TO-TEXT")
    print("="*40)
    print("\nStarting recording now...")
    
    audio_data, rate, width = record_audio()
    
    save_audio(audio_data, rate, width)
    
    transcribe_and_save(audio_data, rate, width)
    
    plot_waveform(audio_data, rate)

if __name__ == "__main__":
    main()