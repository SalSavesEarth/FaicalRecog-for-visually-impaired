import os
import io
from datetime import datetime
import cv2
import numpy as np
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import face_recognition
import pyttsx3
import threading  # For non-blocking text-to-speech
import time

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Define the path to your service account file
SERVICE_ACCOUNT_FILE = r'C:\Users\97156\Downloads\key.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

# Authenticate using the service account
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)

# Function to get images from Google Drive in memory
def get_images_from_drive():
    images = []
    classNames = []
    folder_id = '1XTx7TXI795GypJmgDtJMahmVIOAGugIf'
    results = drive_service.files().list(
        q=f"'{folder_id}' in parents and mimeType='image/jpeg'",
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print("No files found.")
    else:
        for item in items:
            file_id = item['id']
            file_name = item['name']
            classNames.append(os.path.splitext(file_name)[0])

            # Retrieve image data
            request = drive_service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            fh.seek(0)
            
            # Read image from bytes as a numpy array
            file_bytes = np.asarray(bytearray(fh.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            images.append(img)

    return images, classNames

# Load images from Google Drive
images, classNames = get_images_from_drive()
print(classNames)

# Define the function to encode faces
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

# Encode the known images
encodeListKnown = findEncodings(images)
print('Encoding Complete')

# ESP32-CAM's streaming URL
esp32_cam_url = "http://10.168.169.198:81/stream" #"http://10.168.170.58:81/stream" Update with your ESP32-CAM's IP
cap = cv2.VideoCapture(esp32_cam_url)

# Dictionary to track last announced time for each name
last_announced = {}

# Function to handle text-to-speech in a non-blocking way
def announce_name(name):
    threading.Thread(target=lambda: engine.say(name) or engine.runAndWait()).start()

# Real-time face recognition
while True:
    success, img = cap.read()
    if not success:
        print("Failed to read from the ESP32-CAM")
        break

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()

            # Announce only if not announced recently (3-second interval)
            current_time = time.time()
            if name not in last_announced or current_time - last_announced[name] > 3:
                announce_name(f"{name} is here")
                last_announced[name] = current_time

            # Draw bounding box and name label on the image
            y1, x2, y2, x1 = [coord * 4 for coord in faceLoc]
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow('ESP32-CAM Stream', img)
    if cv2.waitKey(1) == 27:  # Press 'Esc' key to exit
        break

cap.release()
cv2.destroyAllWindows()
