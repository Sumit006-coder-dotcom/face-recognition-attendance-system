# takeimage.py
import os
import cv2
import csv
import pandas as pd
from datetime import datetime

def capture_images_for_enrollment(enrollment, name, haarcascade_path, trainimage_path,
                                  subject, start_time, end_time, num_samples=30):
    """
    Capture face images for a new enrollment and save them to:
      trainimage_path/<enrollment>_<name>/{name}_{enrollment}_1.jpg ...
    Also append student details to StudentDetails/studentdetails.csv and StudentDetails/Students.xlsx
    start_time & end_time expected as "HH:MM" strings.
    Returns True if images were captured, False otherwise.
    """
    enrollment = str(enrollment).strip()
    name = str(name).strip()
    if not enrollment.isdigit():
        print("[ERROR] Enrollment must be numeric.")
        return False
    if not name:
        print("[ERROR] Name cannot be empty.")
        return False

    # check haarcascade
    if not os.path.exists(haarcascade_path):
        print(f"[ERROR] Haarcascade not found at {haarcascade_path}")
        return False

    os.makedirs(trainimage_path, exist_ok=True)
    save_dir = os.path.join(trainimage_path, f"{enrollment}_{name}")
    os.makedirs(save_dir, exist_ok=True)

    detector = cv2.CascadeClassifier(haarcascade_path)
    if detector.empty():
        print("[ERROR] Failed to load Haarcascade classifier.")
        return False

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("[ERROR] Camera not accessible.")
        return False

    sampleNum = 0
    print(f"[INFO] Starting capture for {name} ({enrollment}). Press 'q' to stop early.")

    while True:
        ret, img = cam.read()
        if not ret:
            continue
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            sampleNum += 1
            face = gray[y:y+h, x:x+w]
            filename = os.path.join(save_dir, f"{name}_{enrollment}_{sampleNum}.jpg")
            cv2.imwrite(filename, face)
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(img, f"{sampleNum}/{num_samples}", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        cv2.imshow("Register - Press 'q' to stop", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if sampleNum >= num_samples:
            break

    cam.release()
    cv2.destroyAllWindows()
    print(f"[INFO] Captured {sampleNum} images for {enrollment}_{name} at {save_dir}")

    # Save to CSV
    studentdetails_dir = os.path.join("StudentDetails")
    os.makedirs(studentdetails_dir, exist_ok=True)
    studentdetails_path = os.path.join(studentdetails_dir, "studentdetails.csv")

    already = False
    if os.path.exists(studentdetails_path):
        with open(studentdetails_path, "r", newline="", encoding="utf-8") as f:
            for row in f:
                if row.strip().startswith(f"{enrollment},"):
                    already = True
                    break

    if not already:
        with open(studentdetails_path, "a", newline="", encoding="utf-8") as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow([enrollment, name, subject, start_time, end_time])

    # Save/update Excel Students.xlsx
    excel_path = os.path.join(studentdetails_dir, "Students.xlsx")
    row = {"Enrollment": int(enrollment), "Name": name, "Subject": subject,
           "Start": start_time, "End": end_time}
    if os.path.exists(excel_path):
        try:
            old = pd.read_excel(excel_path)
            # avoid duplicates on enrollment
            if int(enrollment) in old['Enrollment'].values:
                print("[INFO] Enrollment already in Students.xlsx — updating record.")
                old.loc[old['Enrollment'] == int(enrollment), ['Name','Subject','Start','End']] = \
                    [name, subject, start_time, end_time]
                old.to_excel(excel_path, index=False)
            else:
                new = pd.concat([old, pd.DataFrame([row])], ignore_index=True)
                new.to_excel(excel_path, index=False)
        except Exception as e:
            print(f"[WARNING] Could not update Students.xlsx: {e}. Recreating file.")
            pd.DataFrame([row]).to_excel(excel_path, index=False)
    else:
        pd.DataFrame([row]).to_excel(excel_path, index=False)

    return sampleNum > 0
import tkinter as tk
from tkinter import messagebox
from tkinter import *
from tkinter import simpledialog
import os
from PIL import Image, ImageTk
from takeImage import capture_images_for_enrollment     