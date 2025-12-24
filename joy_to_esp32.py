import pygame
import socket
import time

# ============================
# CONFIG
# ============================

# When ESP32 is AP, its IP is usually 192.168.4.1
ESP32_IP = "192.168.4.1"
ESP32_PORT = 4210

SEND_INTERVAL = 0.05  # seconds (20 Hz)

# ============================
# INIT
# ============================

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No joystick detected. Plug it in and try again.")
    raise SystemExit

js = pygame.joystick.Joystick(0)
js.init()
print("Joystick connected:", js.get_name())

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"Sending UDP to {ESP32_IP}:{ESP32_PORT}")

# ============================
# MAIN LOOP
# ============================

try:
    while True:
        pygame.event.pump()

        raw_y = js.get_axis(1)  # up = -1, down = +1 (usually)

        if raw_y <= -0.5:
            y_state = -1
        elif raw_y >= 0.5:
            y_state = 1
        else:
            y_state = 0

        msg = str(y_state).encode()
        sock.sendto(msg, (ESP32_IP, ESP32_PORT))

        print(f"raw_y={raw_y:.2f} -> state={y_state}")

        time.sleep(SEND_INTERVAL)

except KeyboardInterrupt:
    print("\nExiting...")
finally:
    pygame.joystick.quit()
    pygame.quit()
