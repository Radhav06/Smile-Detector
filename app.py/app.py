# Smile Detctor and automatically Snapshot Clicker - Voice - Controlled 
from flask import Flask, render_template, request, jsonify  # Importing Flask and its utilities
import cv2  # OpenCV for image processing
import threading  # To handle background tasks (e.g., camera operation)
import time  # For timestamps to save snapshots
import pyttsx3  # Text-to-speech module to provide voice feedback
import speech_recognition as sr  # For voice command recognition

# Initialize Flask app
app = Flask(__name__)

# Global variables to track the camera state
camera_running = False  # Whether the camera is active
video_capture = None  # To store the VideoCapture object

# Function to detect smiles using OpenCV
def detect_smile():
    """
    Continuously captures video frames, detects faces and smiles, 
    and saves a snapshot when a smile is detected.
    """
    global camera_running, video_capture

    # Load pre-trained classifiers for face and smile detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

    while camera_running:  # Run only if the camera is active
        ret, frame = video_capture.read()  # Capture a frame from the webcam
        if not ret:  # If the frame is not captured correctly, stop
            break

        # Convert the frame to grayscale for better performance in detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        # Loop through detected faces
        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]  # Region of interest in grayscale
            roi_color = frame[y:y+h, x:x+w]  # Region of interest in color

            # Detect smiles in the region of interest (face area)
            smiles = smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.7, minNeighbors=22)

            # If a smile is detected, save the snapshot
            if len(smiles) > 0:
                cv2.imwrite(f"smile_{int(time.time())}.jpg", frame)  # Save image with a timestamp
                cv2.putText(frame, "Smile Detected!", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Display the live video feed with detections
        cv2.imshow("Smile Detector", frame)

        # Exit the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and close the video window when done
    video_capture.release()
    cv2.destroyAllWindows()

# Function to start the camera and run the smile detection
def start_camera():
    """
    Starts the webcam and initializes smile detection in a background thread.
    """
    global camera_running, video_capture
    if not camera_running:  # Only start if the camera is not already running
        camera_running = True
        video_capture = cv2.VideoCapture(0)  # Open the webcam (default camera is index 0)
        threading.Thread(target=detect_smile).start()  # Run smile detection in a separate thread

# Function to stop the camera
def stop_camera():
    """
    Stops the webcam and terminates the smile detection process.
    """
    global camera_running
    camera_running = False  # This will break the detection loop in `detect_smile`

# Function to listen for voice commands
def listen_for_command():
    """
    Listens for specific voice commands: 'start camera' or 'stop camera'.
    Executes the appropriate action based on the command.
    """
    recognizer = sr.Recognizer()  # Initialize speech recognizer
    engine = pyttsx3.init()  # Initialize text-to-speech engine

    # Provide instructions to the user via voice
    engine.say("Say 'start camera' to begin or 'stop camera' to end.")
    engine.runAndWait()

    with sr.Microphone() as source:  # Use the microphone for input
        try:
            audio = recognizer.listen(source)  # Listen to the user's voice
            command = recognizer.recognize_google(audio).lower()  # Convert speech to text

            # Execute commands based on recognized text
            if "start camera" in command:
                start_camera()  # Start the camera
            elif "stop camera" in command:
                stop_camera()  # Stop the camera
            else:
                # Handle invalid commands
                engine.say("Invalid command. Please say 'start camera' or 'stop camera'.")
                engine.runAndWait()
        except sr.UnknownValueError:
            # Handle cases where the speech is not understood
            engine.say("Sorry, I did not understand. Please try again.")
            engine.runAndWait()

# Define a route for the home page
@app.route('/')
def index():
    """
    Serves the HTML page for the frontend.
    """
    return render_template('index.html')  # Render the HTML file located in the `templates` folder

# Define a route to trigger voice commands
@app.route('/voice-command', methods=['POST'])
def voice_command():
    """
    Endpoint to trigger the voice command listener.
    """
    threading.Thread(target=listen_for_command).start()  # Run the voice listener in a background thread
    return jsonify({"status": "Listening for commands"})  # Respond with a status message

# Start the Flask server
if __name__ == '__main__':
    """
    Runs the Flask app in debug mode for development purposes.
    """
    app.run(debug=True)
