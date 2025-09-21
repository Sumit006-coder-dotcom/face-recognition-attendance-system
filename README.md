# Face Recognition Attendance System  

An *automated student attendance system* using *Python, OpenCV, Haar Cascade, Pandas, NumPy, Pillow, OpenPyXL, and pyttsx3*.  
This project captures student faces, marks attendance automatically, and stores the data in Excel format with text-to-speech feedback.  

---

## Table of Contents  
- [Overview](#overview)  
- [Features](#features)  
- [Tech Stack](#tech-stack)  
- [Project Workflow](#project-workflow)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Folder Structure](#folder-structure)  
- [Sample Output](#sample-output)  
- [Future Improvements](#future-improvements)  
- [Acknowledgments](#acknowledgments)  

---

## Overview  
This project was developed as part of my *Smart India Hackathon 2025* journey.  
We started with *519 teams, progressed to the **top 200, and finally made it to the **pre-qualifiers (top 130 teams)*.  

The system uses *face recognition* to automate the attendance process, making it faster, accurate, and paperless.  

---

## Features  
- *Automatic Attendance:* Detects and marks attendance using live camera feed  
- *Student Registration:* Stores enrollment number, name, subject, class timings  
- *Excel Reports:* Saves attendance data in Excel format using openpyxl  
- *Image Handling:* Uses Pillow for image operations  
- *Voice Feedback:* Announces attendance using pyttsx3  
- *Lightweight:* Uses Haar Cascade (OpenCV) for fast face detection  
- *Simple Setup:* Minimal dependencies, easy to run  

---

## Tech Stack  
- *Programming Language:* Python  
- *Libraries:*  
  - opencv-python / opencv-contrib-python – Face detection & recognition  
  - Haar Cascade – Pre-trained classifier for face detection  
  - pandas – Data storage & manipulation  
  - numpy – Efficient numerical operations  
  - openpyxl – Excel file handling  
  - pillow – Image processing  
  - pyttsx3 – Text-to-speech feedback  
- *Output:* Excel File (.xlsx)  

---

## Project Workflow  

1️. *Student Registration:*  
Students register with:
- Enrollment Number  
- Name  
- Subject  
- Class Start & End Time  

2️. *Face Detection & Recognition:*  
- Camera feed opens  
- Haar Cascade detects faces  
- If recognized, attendance is marked  
- Voice confirmation using pyttsx3  

3️. *Data Storage:*  
- Attendance is logged into Excel  
- Data can be accessed later by teachers/admin  

---

## Installation  

Clone the repository:  
```bash
git clone https://github.com/your-username/face-recognition-attendance-system.git
cd face-recognition-attendance-system
