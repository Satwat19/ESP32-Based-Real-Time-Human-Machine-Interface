# import tkinter as tk
# from tkinter import ttk
# import threading
# import time
# import cv2
# import pygame
# import requests
# import json
# import sounddevice as sd
# import queue
# import socket
# import os
# from vosk import Model, KaldiRecognizer

# # ============================
# # GLOBAL SETTINGS
# # ============================
# # IMPORTANT: Check Serial Monitor for the actual IP
# ESP32_IP_RAW = "10.128.252.10"  # <--- REPLACE WITH YOUR ESP32 IP ADDRESS
# ESP32_PORT = 4210               

# model_path = "voice/vosk_model"        
# sample_rate = 16000
# q = queue.Queue()                      

# # ============================
# # CAMERA MODE
# # ============================
# def start_camera_feed(text_area, stop_event):
#     url = "http://10.25.49.98:8080/video"   
#     cap = cv2.VideoCapture(url)

#     if not cap.isOpened():
#         if text_area:
#             text_area.delete(1.0, tk.END)
#             text_area.insert(tk.END, "Camera could not open.\n")
#         return

#     if text_area:
#         text_area.delete(1.0, tk.END)
#         text_area.insert(tk.END, "Camera Mode Active... Press 'q' in video window to quit.\n")

#     while not stop_event.is_set():
#         ret, frame = cap.read()
#         if not ret:
#             break
#         cv2.imshow("Mobile Camera", frame)
#         if cv2.waitKey(1) & 0xFF == ord("q"):
#             break

#     cap.release()
#     cv2.destroyAllWindows()
#     print("Camera thread finished")

# # ============================
# # NLP MODE
# # ============================
# def callback(indata, frames, time_info, status):
#     if status:
#         print("Status:", status)
#     q.put(bytes(indata))

# def start_nlp(text_area, stop_event):
#     if not os.path.exists(model_path):
#         if text_area:
#              text_area.insert(tk.END, f"Error: Model not found at {model_path}\n")
#         return

#     grammar = '["start", "stop"]'
#     model = Model(model_path)
#     recognizer = KaldiRecognizer(model, sample_rate, grammar)

#     if text_area:
#         text_area.delete(1.0, tk.END)
#         text_area.insert(tk.END, "NLP Mode Active... Say 'start' or 'stop'.\n")

#     with sd.RawInputStream(samplerate=sample_rate, blocksize=8000, dtype="int16", channels=1, callback=callback):
#         while not stop_event.is_set():
#             try:
#                 data = q.get(timeout=0.5)
#             except queue.Empty:
#                 continue

#             if recognizer.AcceptWaveform(data):
#                 result = json.loads(recognizer.Result())
#                 text = result.get("text", "").strip()
                
#                 if text == "start":
#                     if text_area:
#                         text_area.delete(1.0, tk.END)
#                         text_area.insert(tk.END, "Voice Command: START\n")
#                 elif text == "stop":
#                     if text_area:
#                         text_area.delete(1.0, tk.END)
#                         text_area.insert(tk.END, "Voice Command: STOP\n")

# # ============================
# # JOYSTICK MODE (UDP) - FIXED
# # ============================
# def start_joystick_data(text_area, stop_event):
#     pygame.init()
#     pygame.joystick.init()

#     if pygame.joystick.get_count() == 0:
#         if text_area:
#             text_area.delete(1.0, tk.END)
#             text_area.insert(tk.END, "No joystick detected.\n")
#         return

#     js = pygame.joystick.Joystick(0)
#     js.init()

#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
#     print("Joystick connected:", js.get_name())
    
#     # Counter to limit GUI updates (prevents lag)
#     update_counter = 0 

#     while not stop_event.is_set():
#         pygame.event.pump()
        
#         # Axis 1 (Left Stick Y): 
#         # Usually: UP = -1.0, DOWN = +1.0
#         # We send this raw value to ESP32
#         raw_y = js.get_axis(1)
#         y_val = round(raw_y, 2) 

#         # Send to ESP32 via UDP
#         try:
#             message = str(y_val).encode()
#             sock.sendto(message, (ESP32_IP_RAW, ESP32_PORT))
#         except Exception as e:
#             print("Error sending UDP:", e)

#         # FIX: Update GUI to show coordinates
#         update_counter += 1
#         if text_area and update_counter % 5 == 0: # Update every 5th loop (approx every 250ms)
#             # We use try/except because updating GUI from a thread can sometimes cause issues
#             try:
#                 text_area.delete(1.0, tk.END)
#                 status_msg = f"Joystick Connected: {js.get_name()}\n"
#                 status_msg += f"Target IP: {ESP32_IP_RAW}\n"
#                 status_msg += f"---------------------------\n"
#                 status_msg += f"Y-AXIS VALUE: {y_val}\n" # <--- THIS DISPLAYS THE COORDINATE
                
#                 # Logic Feedback for user
#                 if y_val < -0.2:
#                     status_msg += "Status: MOVING FORWARD"
#                 elif y_val > 0.2:
#                     status_msg += "Status: MOVING BACKWARD"
#                 else:
#                     status_msg += "Status: STOPPED (Deadzone)"
                    
#                 text_area.insert(tk.END, status_msg)
#             except:
#                 pass
        
#         # Reset counter to avoid overflow
#         if update_counter > 100:
#             update_counter = 0

#         time.sleep(0.05) 

#     print("Joystick thread finished")

# # ============================
# # GUI APP
# # ============================
# class App:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Robot HMI Interface")
#         self.root.geometry("800x600")
        
#         self.frame = ttk.Frame(root, padding=20)
#         self.frame.pack(fill="both", expand=True)

#         self.nlp_button = ttk.Button(self.frame, text="NLP Mode", command=self.set_nlp_mode, width=20)
#         self.manual_button = ttk.Button(self.frame, text="Manual Mode", command=self.set_manual_mode, width=20)
#         self.camera_button = ttk.Button(self.frame, text="Camera Mode", command=self.set_camera_mode, width=20)

#         self.nlp_button.grid(row=0, column=0, padx=20, pady=10)
#         self.manual_button.grid(row=0, column=1, padx=20, pady=10)
#         self.camera_button.grid(row=0, column=2, padx=20, pady=10)

#         self.text_area = tk.Text(self.frame, width=80, height=10, font=("Helvetica", 14)) # Increased font size
#         self.text_area.grid(row=1, column=0, columnspan=3, padx=20, pady=20)

#         self.stop_event = threading.Event()
#         self.thread = None

#     def stop_previous(self):
#         self.stop_event.set()
#         if self.thread and self.thread.is_alive():
#             self.thread.join(timeout=0.5)
#         self.stop_event = threading.Event()
#         self.thread = None

#     def set_nlp_mode(self):
#         self.stop_previous()
#         self.text_area.delete(1.0, tk.END)
#         self.text_area.insert(tk.END, "Starting NLP Mode...\n")
#         self.thread = threading.Thread(target=start_nlp, args=(self.text_area, self.stop_event), daemon=True)
#         self.thread.start()

#     def set_manual_mode(self):
#         self.stop_previous()
#         self.text_area.delete(1.0, tk.END)
#         self.text_area.insert(tk.END, "Starting Joystick Mode...\n")
#         self.thread = threading.Thread(target=start_joystick_data, args=(self.text_area, self.stop_event), daemon=True)
#         self.thread.start()

#     def set_camera_mode(self):
#         self.stop_previous()
#         self.text_area.delete(1.0, tk.END)
#         self.text_area.insert(tk.END, "Starting Camera Mode...\n")
#         self.thread = threading.Thread(target=start_camera_feed, args=(self.text_area, self.stop_event), daemon=True)
#         self.thread.start()

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = App(root)
#     root.mainloop()




import tkinter as tk
from tkinter import ttk
import threading
import time
import cv2
import pygame
import requests
import json
import sounddevice as sd
import queue
import socket
import os
from vosk import Model, KaldiRecognizer

# ============================
# GLOBAL SETTINGS
# ============================
# Set this to the IP printed by your ESP32 in Serial Monitor
ESP32_IP_RAW = "10.128.252.10"   # <--- REPLACE THIS
ESP32_PORT = 4210                

model_path = "voice/vosk_model"        
sample_rate = 16000
q = queue.Queue()                      

LOG_FILE_PATH = "joystick_log.txt"     # log file in same folder as this script

# ============================
# CAMERA MODE
# ============================
def start_camera_feed(text_area, stop_event):
    url = "http://10.25.49.98:8080/video"   # your phone IP cam URL
    cap = cv2.VideoCapture(url)

    if not cap.isOpened():
        if text_area:
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, "Camera could not open.\n")
        return

    if text_area:
        text_area.delete(1.0, tk.END)
        text_area.insert(
            tk.END,
            "Camera Mode Active... Press 'q' in video window to quit.\n"
        )

    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Mobile Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Camera thread finished")

# ============================
# NLP MODE
# ============================
def callback(indata, frames, time_info, status):
    if status:
        print("Status:", status)
    q.put(bytes(indata))

def start_nlp(text_area, stop_event):
    if not os.path.exists(model_path):
        if text_area:
             text_area.insert(tk.END, f"Error: Model not found at {model_path}\n")
        return

    grammar = '["start", "stop"]'
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, sample_rate, grammar)

    if text_area:
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, "NLP Mode Active... Say 'start' or 'stop'.\n")

    with sd.RawInputStream(
        samplerate=sample_rate,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=callback
    ):
        while not stop_event.is_set():
            try:
                data = q.get(timeout=0.5)
            except queue.Empty:
                continue

            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip()
                
                if text == "start":
                    if text_area:
                        text_area.delete(1.0, tk.END)
                        text_area.insert(tk.END, "Voice Command: START\n")
                elif text == "stop":
                    if text_area:
                        text_area.delete(1.0, tk.END)
                        text_area.insert(tk.END, "Voice Command: STOP\n")

# ============================
# JOYSTICK MODE (UDP + LOGGING)
# ============================
def start_joystick_data(text_area, stop_event):
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        if text_area:
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, "No joystick detected.\n")
        return

    js = pygame.joystick.Joystick(0)
    js.init()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    print("Joystick connected:", js.get_name())

    log_file = open(LOG_FILE_PATH, "a", buffering=1)  # line-buffered

    if text_area:
        text_area.delete(1.0, tk.END)
        text_area.insert(
            tk.END,
            f"Starting Joystick Mode...\n"
            f"Logging to: {os.path.abspath(LOG_FILE_PATH)}\n"
            f"Sending UDP to {ESP32_IP_RAW}:{ESP32_PORT}\n"
        )

    update_counter = 0

    try:
        while not stop_event.is_set():
            pygame.event.pump()

            # Axis 0: X, Axis 1: Y
            raw_x = js.get_axis(0)
            raw_y = js.get_axis(1)

            # Rounded values for display only
            x_val = round(raw_x, 2)
            y_val = round(raw_y, 2)

            # === QUANTIZE Y to -1 / 0 / +1 ===
            # Forward (up): raw_y <= -0.5  => -1
            # Backward (down): raw_y >= 0.5 => +1
            # Center: -0.5 < raw_y < 0.5    => 0
            if raw_y <= -0.5:
                y_state = -1
            elif raw_y >= 0.5:
                y_state = 1
            else:
                y_state = 0

            # 1) SEND STATE TO ESP32
            try:
                message = str(y_state).encode()  # "-1", "0", or "1"
                sock.sendto(message, (ESP32_IP_RAW, ESP32_PORT))
            except Exception as e:
                print("Error sending UDP:", e)

            # 2) LOG TO FILE (timestamp, y_state)
            timestamp = time.time()
            log_file.write(f"{timestamp:.3f},{y_state}\n")

            # 3) UPDATE GUI
            update_counter += 1
            if text_area and update_counter % 5 == 0:  # ~250 ms
                try:
                    text_area.delete(1.0, tk.END)
                    status_msg = f"Joystick Connected: {js.get_name()}\n"
                    status_msg += f"Target IP: {ESP32_IP_RAW}\n"
                    status_msg += f"Log File: {os.path.abspath(LOG_FILE_PATH)}\n"
                    status_msg += "---------------------------\n"
                    status_msg += f"RAW X: {x_val:.2f}\n"
                    status_msg += f"RAW Y: {y_val:.2f}\n"
                    status_msg += f"Y STATE SENT: {y_state}\n\n"

                    if y_state == -1:
                        status_msg += "Status: MOVING FORWARD (Y_STATE = -1)\n"
                    elif y_state == 1:
                        status_msg += "Status: MOVING BACKWARD (Y_STATE = 1)\n"
                    else:
                        status_msg += "Status: STOPPED (Y_STATE = 0)\n"

                    text_area.insert(tk.END, status_msg)
                except:
                    pass

            if update_counter > 100:
                update_counter = 0

            time.sleep(0.05)  # 20 Hz
    finally:
        log_file.close()
        print("Joystick thread finished, log file closed.")

# ============================
# GUI APP
# ============================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Robot HMI Interface")
        self.root.geometry("800x600")
        
        self.frame = ttk.Frame(root, padding=20)
        self.frame.pack(fill="both", expand=True)

        self.nlp_button = ttk.Button(
            self.frame, text="NLP Mode", command=self.set_nlp_mode, width=20
        )
        self.manual_button = ttk.Button(
            self.frame, text="Manual Mode", command=self.set_manual_mode, width=20
        )
        self.camera_button = ttk.Button(
            self.frame, text="Camera Mode", command=self.set_camera_mode, width=20
        )

        self.nlp_button.grid(row=0, column=0, padx=20, pady=10)
        self.manual_button.grid(row=0, column=1, padx=20, pady=10)
        self.camera_button.grid(row=0, column=2, padx=20, pady=10)

        self.text_area = tk.Text(
            self.frame, width=80, height=10, font=("Helvetica", 14)
        )
        self.text_area.grid(row=1, column=0, columnspan=3, padx=20, pady=20)

        self.stop_event = threading.Event()
        self.thread = None

    def stop_previous(self):
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.5)
        self.stop_event = threading.Event()
        self.thread = None

    def set_nlp_mode(self):
        self.stop_previous()
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "Starting NLP Mode...\n")
        self.thread = threading.Thread(
            target=start_nlp,
            args=(self.text_area, self.stop_event),
            daemon=True
        )
        self.thread.start()

    def set_manual_mode(self):
        self.stop_previous()
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "Starting Joystick Mode...\n")
        self.thread = threading.Thread(
            target=start_joystick_data,
            args=(self.text_area, self.stop_event),
            daemon=True
        )
        self.thread.start()

    def set_camera_mode(self):
        self.stop_previous()
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "Starting Camera Mode...\n")
        self.thread = threading.Thread(
            target=start_camera_feed,
            args=(self.text_area, self.stop_event),
            daemon=True
        )
        self.thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
