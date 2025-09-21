import pandas as pd
from glob import glob
import os
import tkinter as tk
from tkinter import *
import csv

def subjectchoose(text_to_speech):
    def calculate_attendance():
        Subject = tx.get().strip()
        if Subject == "":
            t = 'Please enter the subject name.'
            text_to_speech(t)
            return

        folder_path = os.path.join("Attendance", Subject)
        if not os.path.exists(folder_path):
            t = f"No attendance folder found for subject: {Subject}"
            text_to_speech(t)
            return

        # Find all CSV files for this subject
        filenames = glob(os.path.join(folder_path, f"{Subject}*.csv"))
        if len(filenames) == 0:
            t = f"No attendance CSVs found for subject: {Subject}"
            text_to_speech(t)
            return

        # Read CSVs into DataFrames
        dfs = [pd.read_csv(f) for f in filenames]
        newdf = dfs[0]
        for i in range(1, len(dfs)):
            newdf = newdf.merge(dfs[i], how="outer")
        newdf.fillna(0, inplace=True)

        # Calculate attendance %
        newdf["Attendance"] = newdf.iloc[:, 2:].mean(axis=1).apply(lambda x: f"{int(round(x*100))}%")

        # Save merged attendance
        output_file = os.path.join(folder_path, "attendance.csv")
        newdf.to_csv(output_file, index=False)

        # Display in Tkinter
        root = tk.Tk()
        root.title("Attendance of " + Subject)
        root.configure(background="black")

        with open(output_file) as file:
            reader = csv.reader(file)
            for r_idx, row in enumerate(reader):
                for c_idx, val in enumerate(row):
                    label = tk.Label(
                        root,
                        width=12,
                        height=1,
                        fg="yellow",
                        font=("times", 15, "bold"),
                        bg="black",
                        text=val,
                        relief=tk.RIDGE,
                    )
                    label.grid(row=r_idx, column=c_idx)

        root.mainloop()

    # Tkinter UI
    subject = tk.Tk()
    subject.title("Subject Attendance")
    subject.geometry("580x320")
    subject.resizable(0, 0)
    subject.configure(background="black")

    titl = tk.Label(subject, bg="black", relief=RIDGE, bd=10, font=("arial", 30))
    titl.pack(fill=X)

    tk.Label(
        subject,
        text="Which Subject of Attendance?",
        bg="black",
        fg="green",
        font=("arial", 25),
    ).place(x=100, y=12)

    tk.Label(
        subject,
        text="Enter Subject",
        width=10,
        height=2,
        bg="black",
        fg="yellow",
        bd=5,
        relief=RIDGE,
        font=("times new roman", 15),
    ).place(x=50, y=100)

    tx = tk.Entry(
        subject,
        width=15,
        bd=5,
        bg="black",
        fg="yellow",
        relief=RIDGE,
        font=("times", 30, "bold"),
    )
    tx.place(x=190, y=100)

    fill_a = tk.Button(
        subject,
        text="View Attendance",
        command=calculate_attendance,
        bd=7,
        font=("times new roman", 15),
        bg="black",
        fg="yellow",
        height=2,
        width=12,
        relief=RIDGE,
    )
    fill_a.place(x=195, y=170)

    def check_sheets():
        sub = tx.get().strip()
        folder_path = os.path.join("Attendance", sub)
        if not os.path.exists(folder_path):
            text_to_speech(f"No folder found for subject: {sub}")
            return
        os.startfile(folder_path)

    attf = tk.Button(
        subject,
        text="Check Sheets",
        command=check_sheets,
        bd=7,
        font=("times new roman", 15),
        bg="black",
        fg="yellow",
        height=2,
        width=10,
        relief=RIDGE,
    )
    attf.place(x=360, y=170)

    subject.mainloop()
