Facial Recognition Smart Glasses for Visually Impaired Assistance
This project is an AI-powered facial recognition assistance system designed to help visually impaired individuals identify people around them in real time.
The system uses an ESP32-CAM module to stream live video to a Python-based computer vision application. Facial recognition is performed using the face_recognition library and OpenCV, while known face datasets are dynamically retrieved from Google Drive using the Google Drive API.
When a known face is detected, the system announces the person’s name through text-to-speech audio feedback, allowing users to recognize nearby individuals without visual interaction.

Features: 
Real-time facial recognition
ESP32-CAM live video streaming
Google Drive cloud image database integration
Voice-based name announcements using text-to-speech
Non-blocking speech processing with multithreading
Automatic face encoding and matching
OpenCV live detection interface

Technologies Used:
Python
OpenCV
face_recognition
ESP32-CAM
Google Drive API
NumPy
pyttsx3
Multithreading

How It Works:
The ESP32-CAM streams live video over Wi-Fi.
The system downloads authorized face images from Google Drive.
Face encodings are generated for all known individuals.
Incoming video frames are analyzed in real time.
When a face match is detected, the system announces the detected person's name using audio output.

Potential Applications:
Assistive technology for visually impaired individuals
Smart wearable AI systems
Security and identity verification
Human-aware embedded systems
