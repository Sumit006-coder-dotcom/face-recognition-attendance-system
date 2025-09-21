# automaticattendance.py
import os
import cv2
import csv
import pandas as pd
import datetime
import time
import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import *
from trainimage import TrainImage
from takeImage import capture_images_for_enrollment

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
haarcasecade_path = os.path.join(BASE_DIR, "haarcascade_frontalface_default.xml")
trainimagelabel_path = os.path.join(BASE_DIR, "TrainingImageLabel", "Trainner.yml")
trainimage_path = os.path.join(BASE_DIR, "TrainingImage")
studentdetail_excel = os.path.join(BASE_DIR, "StudentDetails", "Students.xlsx")
attendance_excel = os.path.join(BASE_DIR, "Attendance.xlsx")

CONFIDENCE_THRESHOLD = 70  # LBPH: lower is better match

def save_attendance_records(records, subject, filename=attendance_excel):
    """
    records: list of dicts with keys: ID, Name, Start, End, Duration (min), Status, Date, Subject
    """
    df_new = pd.DataFrame(records)
    if os.path.exists(filename):
        try:
            old = pd.read_excel(filename)
            final = pd.concat([old, df_new], ignore_index=True)
        except Exception as e:
            print(f"[WARN] Could not read existing attendance workbook: {e}. Overwriting.")
            final = df_new
    else:
        final = df_new
    final.to_excel(filename, index=False)
    print(f"[INFO] Attendance appended to {filename}")

def subjectChoose(ignore_tts=None):
    def FillAttendance():
        sub = tx.get().strip()
        if not sub:
            messagebox.showwarning("Input required", "Enter subject name")
            return

        if not os.path.exists(haarcasecade_path):
            messagebox.showerror("Missing file", "Haarcascade XML not found.")
            return

        model_exists = os.path.exists(trainimagelabel_path)
        if not os.path.exists(studentdetail_excel):
            # create empty students file if missing
            os.makedirs(os.path.dirname(studentdetail_excel), exist_ok=True)
            pd.DataFrame(columns=["Enrollment","Name","Subject","Start","End"]).to_excel(studentdetail_excel, index=False)

        students_df = pd.read_excel(studentdetail_excel)
        # filter students for this subject
        subject_students = students_df[students_df['Subject'].astype(str).str.strip().str.lower() == sub.strip().lower()]

        if subject_students.empty:
            messagebox.showinfo("No students", f"No registered students for subject '{sub}'. You can still register unknown faces during attendance.")
        else:
            print(f"[INFO] {len(subject_students)} students registered for subject {sub}")

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        if model_exists:
            try:
                recognizer.read(trainimagelabel_path)
            except Exception as e:
                print(f"[WARN] Could not load model: {e}")

        faceCascade = cv2.CascadeClassifier(haarcasecade_path)
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            messagebox.showerror("Camera", "Cannot open camera")
            return

        detected_times = {}  # enrollment -> {'Name':..., 'Start': 'HH:MM', 'End': 'HH:MM', 'first_seen': datetime, 'last_seen': datetime}

        start_ts = time.time()
        WINDOW_SECONDS = 20

        unknown_prompted = False

        while True:
            ret, frame = cam.read()
            if not ret:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(gray, 1.2, 5)

            for (x, y, w, h) in faces:
                roi = gray[y:y+h, x:x+w]
                matched = False
                matched_id = None
                matched_name = "Unknown"

                if model_exists:
                    try:
                        Id, conf = recognizer.predict(roi)
                    except Exception as e:
                        Id, conf = None, 999
                    if conf < CONFIDENCE_THRESHOLD:
                        matched = True
                        matched_id = int(Id)
                        # find name from Excel/CSV
                        row = students_df[students_df['Enrollment'] == matched_id]
                        if not row.empty:
                            matched_name = str(row.iloc[0]['Name'])
                        else:
                            matched_name = "Unknown"

                if matched:
                    cv2.rectangle(frame, (x,y),(x+w,y+h),(0,255,0),2)
                    cv2.putText(frame, f"{matched_id}-{matched_name}", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0),2)
                    now_dt = datetime.datetime.now()
                    if matched_id not in detected_times:
                        # find subject timing for this student if exists
                        row = students_df[students_df['Enrollment'] == matched_id]
                        if not row.empty:
                            st = str(row.iloc[0]['Start'])
                            et = str(row.iloc[0]['End'])
                        else:
                            st, et = "00:00", "23:59"
                        detected_times[matched_id] = {'Name': matched_name, 'Start': st, 'End': et,
                                                     'first_seen': now_dt, 'last_seen': now_dt}
                    else:
                        detected_times[matched_id]['last_seen'] = now_dt
                else:
                    # Unknown face - offer registration once per session
                    cv2.rectangle(frame, (x,y),(x+w,y+h),(0,0,255),2)
                    cv2.putText(frame, "Unknown", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255),2)
                    if not unknown_prompted:
                        cam.release()
                        cv2.destroyAllWindows()
                        resp = messagebox.askyesno("Register new person", "Unknown face detected. Do you want to register this person now?")
                        if resp:
                            root = tk.Tk()
                            root.withdraw()
                            enrollment = simpledialog.askstring("Enrollment", "Enter numeric Enrollment (ID):")
                            if enrollment is None or not enrollment.isdigit():
                                messagebox.showwarning("Invalid", "Enrollment must be numeric. Cancelling registration.")
                                cam = cv2.VideoCapture(0)
                                unknown_prompted = True
                                break
                            name = simpledialog.askstring("Name","Enter Name:")
                            if name is None or not name.strip():
                                messagebox.showwarning("Invalid","Name required. Cancelling registration.")
                                cam = cv2.VideoCapture(0)
                                unknown_prompted = True
                                break
                            # ask subject and timing for this student
                            sub_reg = simpledialog.askstring("Subject","Enter Subject for this student:")
                            start_reg = simpledialog.askstring("Start","Enter Start time (HH:MM):")
                            end_reg = simpledialog.askstring("End","Enter End time (HH:MM):")
                            messagebox.showinfo("Capture", f"Capturing images for {name}. Please look at camera.")
                            captured = capture_images_for_enrollment(enrollment, name, haarcasecade_path, trainimage_path,
                                                                    sub_reg or sub, start_reg or "00:00", end_reg or "23:59", num_samples=30)
                            if captured:
                                trained = TrainImage(haarcasecade_path, trainimage_path, trainimagelabel_path, None)
                                if trained:
                                    messagebox.showinfo("Done","Registration and training completed.")
                                    # reload students_df
                                    students_df = pd.read_excel(studentdetail_excel)
                                else:
                                    messagebox.showwarning("Training", "Training failed. Please try training manually.")
                            else:
                                messagebox.showwarning("Capture", "Image capture failed. Try again.")
                            cam = cv2.VideoCapture(0)
                            unknown_prompted = True
                            break
                        else:
                            cam = cv2.VideoCapture(0)
                            unknown_prompted = True
                            break

            cv2.imshow("Filling Attendance...", frame)
            if cv2.waitKey(30) & 0xFF == 27:
                break
            if time.time() - start_ts > WINDOW_SECONDS:
                break

        cam.release()
        cv2.destroyAllWindows()

        # Build records for saving to Excel
        if not detected_times:
            messagebox.showinfo("No attendance", "No recognized faces detected in session.")
            return

        records = []
        for eid, info in detected_times.items():
            first = info['first_seen'].strftime("%H:%M")
            last = info['last_seen'].strftime("%H:%M")
            fmt = "%H:%M"
            try:
                start_allowed = datetime.datetime.strptime(info['Start'], fmt)
                end_allowed = datetime.datetime.strptime(info['End'], fmt)
            except:
                start_allowed = None
                end_allowed = None

            # compute duration in minutes between first and last seen
            duration = int((info['last_seen'] - info['first_seen']).total_seconds() // 60)
            status = "Present"
            if start_allowed and end_allowed:
                now_date = info['last_seen'].date()
                # compare presence interval with allowed interval (we mark present if they were seen at least once within)
                # Simplified: check if first_seen time in allowed interval
                if not (start_allowed.time() <= info['first_seen'].time() <= end_allowed.time()):
                    status = "Absent"

            records.append({
                "ID": eid,
                "Name": info['Name'],
                "Subject": sub,
                "Start": first,
                "End": last,
                "Duration (min)": duration,
                "Status": status,
                "Date": datetime.datetime.now().strftime("%Y-%m-%d")
            })

        save_attendance_records(records, sub)
        messagebox.showinfo("Saved", f"Attendance saved for subject {sub} in {attendance_excel}")

    # UI
    root_win = Tk()
    root_win.title("Subject...")
    root_win.geometry("580x320")
    root_win.resizable(0,0)
    root_win.configure(background="black")
    Label(root_win, bg="black", relief=RIDGE, bd=10, font=("arial",30)).pack(fill=X)
    Label(root_win, text="Enter the Subject Name", bg="black", fg="green", font=("arial",25)).place(x=160,y=12)
    Notifica = Label(root_win, text="", bg="yellow", fg="black", width=40, height=2, font=("times",15,"bold"))
    Label(root_win, text="Enter Subject", width=10, height=2, bg="black", fg="yellow", bd=5, relief=RIDGE, font=("times new roman",15)).place(x=50,y=100)
    tx = Entry(root_win, width=15, bd=5, bg="black", fg="yellow", relief=RIDGE, font=("times",30,"bold"))
    tx.place(x=190,y=100)
    Button(root_win, text="Fill Attendance", command=FillAttendance, bd=7, font=("times new roman",15), bg="black", fg="yellow", height=2, width=12, relief=RIDGE).place(x=195,y=170)
    def open_excel():
        if os.path.exists(attendance_excel):
            os.startfile(attendance_excel)
        else:
            messagebox.showinfo("No file", "Attendance.xlsx not found yet.")
    Button(root_win, text="Check Sheets", command=open_excel, bd=7, font=("times new roman",15), bg="black", fg="yellow", height=2, width=10, relief=RIDGE).place(x=360,y=170)
    root_win.mainloop()
