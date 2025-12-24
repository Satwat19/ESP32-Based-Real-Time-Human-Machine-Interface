import pygame
import requests
import time

ESP32_IP = "http://192.168.10.12"  # 🔁 Replace with your ESP32 IP address

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No joystick detected.")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

print("Joystick connected:", joystick.get_name())

while True:
    pygame.event.pump()
    x_axis = joystick.get_axis(0)
    y_axis = joystick.get_axis(1)

    try:
        response = requests.get(f"{ESP32_IP}/joystick", params={
            "x": round(x_axis, 2),
            "y": round(y_axis, 2)
        })
        print(response.text)
    except Exception as e:
        print("Error:", e)

    time.sleep(10)  # adjust for smoother or faster sending
