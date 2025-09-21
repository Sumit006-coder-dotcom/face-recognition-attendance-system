import cv2
import os
import numpy as np
from PIL import Image

def TrainImage(haarcasecade_path, trainimage_path, trainimagelabel_path, message_label=None):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier(haarcasecade_path)

    faces = []
    ids = []
    labels = {}

    imagePaths = [os.path.join(trainimage_path, f) for f in os.listdir(trainimage_path)]
    current_id = 0

    for folder in imagePaths:
        if not os.path.isdir(folder):
            continue
        folder_name = os.path.basename(folder)
        try:
            enrollment, name = folder_name.split("_", 1)
        except:
            continue
        current_id += 1
        labels[current_id] = name

        for image_file in os.listdir(folder):
            img_path = os.path.join(folder, image_file)
            img = Image.open(img_path).convert('L')
            img_numpy = np.array(img, 'uint8')
            faces.append(img_numpy)
            ids.append(current_id)

    if len(faces) == 0:
        if message_label:
            message_label.config(text="No images found for training.")
        return False

    recognizer.train(faces, np.array(ids))
    os.makedirs(os.path.dirname(trainimagelabel_path), exist_ok=True)
    recognizer.save(trainimagelabel_path)

    # Save label mapping
    with open("labels.txt", "w") as f:
        for id_, name in labels.items():
            f.write(f"{id_},{name}\n")

    if message_label:
        message_label.config(text="Training complete.")
    return True
def capture_images_for_enrollment(enrollment, name, num_samples=50):
    import cv2
    import os
    from datetime import datetime
    import pandas as pd

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    haarcascade_path = os.path.join(BASE_DIR, "haarcascade_frontalface_default.xml")
    trainimage_path = os.path.join(BASE_DIR, "TrainingImage")

    if not enrollment:
        print("[ERROR] Enrollment number cannot be empty.")
        return False
    if not enrollment.isalnum():
        print("[ERROR] Enrollment number must be alphanumeric.")
        return False
    if not name.replace(" ", "").isalpha():
        print("[ERROR] Name must contain only alphabetic characters and spaces.")
        return False
    if len(name.strip().split()) < 2:
        print("[ERROR] Please enter both first and last name.")
        return False
    if len(enrollment) < 4:
        print("[ERROR] Enrollment number must be at least 4 characters long.")
        return False
    if len(name) < 3:
        print("[ERROR] Name must be at least 3 characters long.")
        return False
    if len(name) > 30:
        print("[ERROR] Name is too long. Maximum 30 characters allowed.")
        return False
    if len(enrollment) > 15:
        print("[ERROR] Enrollment number is too long. Maximum 15 characters allowed.")
        return False
    if not name[0].isupper() or not all(part[0].isupper() for part in name.split() if part):
        print("[ERROR] Each part of the name must start with an uppercase letter.")
        return False
    if any(char in "!@#$%^&*()_+=[]{}|;:'\",.<>?/`~" for char in enrollment):
        print("[ERROR] Enrollment number contains invalid special characters.")
        return False
    if any(char.isdigit() for char in name):
        print("[ERROR] Name cannot contain numbers.")
        return False
    if " " in enrollment:
        print("[ERROR] Enrollment number cannot contain spaces.")
        return False
    if not enrollment[0].isalpha():
        print("[ERROR] Enrollment number must start with a letter.")
        return False
    if not name.replace(" ", "").isalpha():
        print("[ERROR] Name must contain only alphabetic characters and spaces.")
        return False
    if any(char in "!@#$%^&*()_+=[]{}|;:'\",.<>?/`~" for char in enrollment):
        print("[ERROR] Enrollment number contains invalid special characters.")
        return False    