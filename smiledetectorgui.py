import cv2  # OpenCV for webcam and image processing
import tkinter as tk  # Tkinter for GUI
from tkinter import Label  # Widgets for GUI
from PIL import Image, ImageTk  # Display OpenCV images in the GUI
import speech_recognition as sr  # Speech recognition for voice commands
import time  # For adding a delay between snapshots

# Load Haar cascades for face and smile detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

class SmileDetectorApp:
    def __init__(self, root):
        self.root = root  # Tkinter root window
        self.root.title("Voice-Controlled Smile Detector")  # Set window title
        self.video_capture = None  # Variable to store the video capture object
        self.running = False  # Flag to control the webcam feed
        self.last_snapshot_time = 0  # Track the last snapshot time to prevent rapid snapshots

        # GUI Widgets
        self.video_label = Label(root)
        self.video_label.pack()  # Label to display the video feed in the GUI

        # Start listening for voice commands
        self.listen_for_commands()

    def start_camera(self):
        """Starts the webcam and begins processing frames."""
        if not self.running:
            self.video_capture = cv2.VideoCapture(0)  # Access the default webcam
            self.running = True  # Set running to True
            print("Camera started.")
            self.update_frame()  # Start updating the video feed

    def stop_camera(self):
        """Stops the webcam and clears the video feed."""
        if self.running:
            self.running = False  # Set running to False to stop the loop
            if self.video_capture:
                self.video_capture.release()  # Release the webcam
            self.video_label.config(image="")  # Clear the video feed in the GUI
            print("Camera stopped.")

    def update_frame(self):
        """Captures frames from the webcam and processes them."""
        if self.running:
            ret, frame = self.video_capture.read()  # Capture a frame from the webcam
            if ret:
                # Convert the frame to grayscale for face and smile detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Detect faces in the frame
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    # Draw a rectangle around the detected face
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                    # Define the region of interest (ROI) for smile detection
                    roi_gray = gray[y:y + h, x:x + w]
                    smiles = smile_cascade.detectMultiScale(roi_gray, 1.8, 20)
                    for (sx, sy, sw, sh) in smiles:
                        # Draw a rectangle around the detected smile
                        cv2.rectangle(frame[y:y + h, x:x + w], (sx, sy), (sx + sw, sy + sh), (0, 255, 0), 2)

                        # Auto-capture snapshot when a smile is detected
                        current_time = time.time()  # Get the current time
                        if current_time - self.last_snapshot_time > 5:  # Delay of 5 seconds between snapshots
                            self.take_snapshot(frame)  # Save the current frame
                            self.last_snapshot_time = current_time  # Update the last snapshot time

                # Convert the frame to RGB format (from BGR) for displaying in Tkinter
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)  # Convert NumPy array to PIL Image
                imgtk = ImageTk.PhotoImage(image=img)  # Convert PIL Image to ImageTk format

                # Update the video feed in the GUI
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)

            # Call this function again after 10 milliseconds
            self.root.after(10, self.update_frame)

    def take_snapshot(self, frame):
        """Saves the given frame as an image file."""
        filename = f"snapshot_{int(time.time())}.jpg"  # Create a unique filename using the timestamp
        cv2.imwrite(filename, frame)  # Save the frame as an image file
        print(f"Snapshot saved as {filename}")  # Print confirmation in the terminal

    def listen_for_commands(self):
        """Continuously listens for voice commands to start or stop the camera."""
        recognizer = sr.Recognizer()  # Create a speech recognition object
        microphone = sr.Microphone()  # Use the default microphone

        def listen():
            print("Listening for commands...")
            while True:
                try:
                    with microphone as source:
                        recognizer.adjust_for_ambient_noise(source)  # Adjust for background noise
                        audio = recognizer.listen(source)  # Listen for a command
                        command = recognizer.recognize_google(audio).lower()  # Convert speech to text
                        print(f"Command received: {command}")

                        if "start camera" in command:
                            self.start_camera()
                        elif "stop camera" in command:
                            self.stop_camera()
                        elif "exit" in command:
                            print("Exiting...")
                            self.root.quit()
                            break

                except sr.UnknownValueError:
                    print("Sorry, I didn't catch that. Please repeat.")
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")

        # Run the listener in a separate thread to avoid blocking the GUI
        import threading
        threading.Thread(target=listen, daemon=True).start()

# Main application execution
root = tk.Tk()  # Create the root Tkinter window
app = SmileDetectorApp(root)  # Create an instance of the application
root.mainloop()  # Start the Tkinter event loop
