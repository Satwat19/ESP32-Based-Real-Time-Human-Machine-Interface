import cv2

# Replace with your actual phone IP and port
url = 'http://192.168.10.8:8080/video'  # Usually this works for IP Webcam

cap = cv2.VideoCapture(url)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    cv2.imshow("Mobile Camera", frame)
    
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
