import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer

q = queue.Queue()
sample_rate = 16000

# Correct model path
model_path = "voice/vosk_model"
model = Model(model_path)

recognizer = KaldiRecognizer(model, sample_rate)

def callback(indata, frames, time, status):
    if status:
        print("Status:", status)
    q.put(bytes(indata))

def listen():
    print("🎙 Listening... Say 'start', 'stop', etc.")
    with sd.RawInputStream(samplerate=sample_rate, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                if text:
                    print("✅ You said:", text)

if __name__ == "__main__":
    listen()
