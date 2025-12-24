import tkinter as tk
import threading
from vision.camera_view import run_camera
from comms.esp_receiver import listen_to_esp
# from voice.voice_command import listen_to_voice  # Optional for later

def start_gui():
    root = tk.Tk()
    root.title("Robot HMI Control")
    root.geometry("500x400")

    display_label = tk.Label(root, text="Select a Mode", font=("Arial", 16))
    display_label.pack(pady=20)

    def show_manual_mode():
        display_label.config(text="Manual Mode: Listening to ESP32...")
        threading.Thread(target=listen_to_esp, args=(display_label,), daemon=True).start()

    def show_nlp_mode():
        display_label.config(text="NLP Mode: Say 'start' or 'stop'")
        # threading.Thread(target=listen_to_voice, args=(display_label,), daemon=True).start()

    btn_manual = tk.Button(root, text="Manual (ESP32)", command=show_manual_mode, width=25)
    btn_manual.pack(pady=10)

    btn_nlp = tk.Button(root, text="NLP (Voice Command)", command=show_nlp_mode, width=25)
    btn_nlp.pack(pady=10)

    # Camera always runs in background
    threading.Thread(target=run_camera, daemon=True).start()

    root.mainloop()
