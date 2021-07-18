import tkinter as tk
from tkinter import *
import numpy as np
import tkinter.ttk as ttk
import tkinter.font as font
import cv2
import os
import csv
from PIL import Image
from PIL import ImageTk
import pandas as pd
import datetime
import time

import pyttsx3

engine = pyttsx3.init()

engine.setProperty('rate', 120)
engine.setProperty('volume', 1.0)

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)


def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        engine.say("Welcome and very Good Morning!")
    elif hour >= 12 and hour < 18:
        engine.say("Welcome and very Good Afternoon!")
    else:
        engine.say("Welcome and very Good Evening")

    engine.say("Lets take your Attendance")
    engine.runAndWait()


wishMe()


def voice2():
    engine.say("Thankyou " + (txt2.get()) +
               " For Submitting Your Attendance " + " Your Unique Id Is " + (txt.get()))
    engine.runAndWait()


def voice3():
    engine.say("Your image has been trained " + (txt2.get()))
    engine.runAndWait()


def voice4():
    engine.say("you look charged up " + (txt2.get()) +
               " it's been great seeing you")
    engine.runAndWait()


def voice5():
    engine.say("Thankyou")
    engine.runAndWait()


window = tk.Tk()
window.title("Face Recognisation Based Attendace System")

window.configure(background='black')

window.attributes('-fullscreen', True)

path = r"BgImage1.jpg"

new_pic = Image.open(path)

# resized = new_pic.resize((2050, 1280), Image.ANTIALIAS)
resized = new_pic.resize((1680, 1050), Image.ANTIALIAS)

deathwing = ImageTk.PhotoImage(resized)

my_label = tk.Label(window, image=deathwing)
my_label.pack()


def clear():
    txt.delete(0, 'end')
    res = ""
    message.configure(text=res)


def clear2():
    txt2.delete(0, 'end')
    res = ""
    message.configure(text=res)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False

# Taking The Images


def TakeImages():
    Id = (txt.get())
    name = (txt2.get())
    if(is_number(Id) and (c.isalpha() or c.isspace() for c in name)):
        cam = cv2.VideoCapture(0)
        harcascadePath = "haarcascade_frontalface_default.xml"
        detector = cv2.CascadeClassifier(harcascadePath)
        sampleNum = 0
        while(True):
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                # incrementing sample number
                sampleNum = sampleNum+1
                # saving the captured face in the dataset folder TrainingImage
                cv2.imwrite("TrainingImage\ " + name + "." + Id +
                            '.' + str(sampleNum) + ".jpg", gray[y:y+h, x:x+w])
                # display the frame
                cv2.imshow('frame', img)
            # wait for 100 miliseconds
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            # break if the sample number is morethan 40
            elif sampleNum > 40:
                break
        cam.release()
        cv2.destroyAllWindows()
        res = "Images Saved for ID : " + Id + " Name : " + name
        row = [Id, name]

        voice2()

        with open('StudentDetails\StudentDetails.csv', 'a+') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        csvFile.close()
        message.configure(text=res)

    else:
        if(is_number(Id)):
            res = "Enter Alphabetical Name"
            message.configure(text=res)
        if(c.isalpha() or c.isspace() for c in name):
            res = "Enter Numeric Id"
            message.configure(text=res)


# Training The Images

def TrainImages():
    Id = (txt.get())
    name = (txt2.get())
    recognizer = cv2.face_LBPHFaceRecognizer.create()
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(harcascadePath)
    faces, Id = getImagesAndLabels("TrainingImage")
    recognizer.train(faces, np.array(Id))
    recognizer.save("TrainingImageLabel\Trainner.yml")
    res = "Image Trained"
    message.configure(text=res)

    voice3()


def getImagesAndLabels(path):
    # get the path of all the files in the folder
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    # print(imagePaths)

    # create empth face list
    faces = []
    # create empty ID list
    Ids = []
    # now looping through all the image paths and loading the Ids and the images
    for imagePath in imagePaths:
        # loading the image and converting it to gray scale
        pilImage = Image.open(imagePath).convert('L')
        # Now we are converting the PIL image into numpy array
        imageNp = np.array(pilImage, 'uint8')
        # getting the Id from the image
        Id = int(os.path.split(imagePath)[-1].split(".")[1])
        # extract the face from the training image sample
        faces.append(imageNp)
        Ids.append(Id)
    return faces, Ids

# Tracking The Images


def TrackImages():
    Id = (txt.get())
    name = (txt2.get())
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("TrainingImageLabel\Trainner.yml")
    harcascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath)
    df = pd.read_csv("StudentDetails\StudentDetails.csv")
    cam = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX
    col_names = ['Id', 'Name', 'Date', 'Time']
    attendance = pd.DataFrame(columns=col_names)
    voice4()
    while True:
        ret, im = cam.read()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.2, 5)
        for(x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x+w, y+h), (178, 255, 255), 2)
            Id, conf = recognizer.predict(gray[y:y+h, x:x+w])
            if(conf < 50):
                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(
                    ts).strftime('%H:%M:%S')
                aa = df.loc[df['Id'] == Id]['Name'].values
                tt = str(Id)+"-"+aa
                attendance.loc[len(attendance)] = [Id, aa, date, timeStamp]

            else:
                Id = 'Unknown'
                tt = str(Id)
            if(conf > 75):
                noOfFile = len(os.listdir("ImagesUnknown"))+1
                cv2.imwrite("ImagesUnknown\Image"+str(noOfFile) +
                            ".jpg", im[y:y+h, x:x+w])
            cv2.putText(im, str(tt), (x, y+h), font, 1, (255, 255, 255), 2)
        attendance = attendance.drop_duplicates(subset=['Id'], keep='first')
        cv2.imshow('im', im)
        if (cv2.waitKey(1) == ord('q')):
            break
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    Hour, Minute, Second = timeStamp.split(":")
    fileName = "Attendance\Attendance_"+date+"_"+Hour+"-"+Minute+"-"+Second+".csv"
    attendance.to_csv(fileName, index=False)
    voice5()
    cam.release()
    cv2.destroyAllWindows()
    # print(attendance)
    res = attendance
    message2.configure(text=res)


lbl = tk.Label(window, text="ENTER ID", width=20, height=1, fg="white",
               borderwidth=4, bg="deepskyblue", font=('kollektif', 15, ' bold '))
lbl.place(x=70, y=360)

txt = tk.Entry(window, width=21, bg="white", fg="black",
               font=('kollektif', 15, ' bold '), borderwidth=3)
txt.place(x=325, y=360)

lbl2 = tk.Label(window, text="ENTER NAME", width=20, fg="white",
                bg="deepskyblue", height=1, borderwidth=4, font=('kollektif', 15, ' bold '))
lbl2.place(x=70, y=650)

txt2 = tk.Entry(window, width=21, bg="white", fg="black",
                font=('kollektif', 15, ' bold '), borderwidth=3)
txt2.place(x=325, y=650)

lbl3 = tk.Label(window, text="STATUS", width=20, fg="white",
                bg="deepskyblue", height=2, font=('kollektif', 15, ' bold '))
lbl3.place(x=1350, y=245)

message = tk.Label(window, text="", bg="white", fg="black", width=35,
                   height=2, activebackground="yellow", font=('kollektif', 15, ' bold '))
message.place(x=1600, y=245)

lbl3 = tk.Label(window, text="ATTENDANCE", width=20, fg="white",
                bg="deepskyblue", height=3, font=('kollektif', 15, ' bold '))
lbl3.place(x=1350, y=745)

message2 = tk.Label(window, text="", fg="black", bg="white",
                    activeforeground="green", width=35, height=3, font=('kollektif', 15, ' bold '))
message2.place(x=1600, y=745)

clearButton = tk.Button(window, text="CLEAR", command=clear, fg="white", bg="deepskyblue",
                        width=19, height=2, activebackground="white", font=('kollektif', 15, ' bold '))
clearButton.place(x=325, y=405)

clearButton2 = tk.Button(window, text="CLEAR", command=clear2, fg="white", bg="deepskyblue",
                         width=19, height=2, activebackground="white", font=('kollektif', 15, ' bold '))
clearButton2.place(x=325, y=575)

takeImg = tk.Button(window, text="CLICK", command=TakeImages, fg="white", bg="deepskyblue",
                    width=15, height=2, activebackground="white", font=('kollektif', 15, ' bold '))
takeImg.place(x=1530, y=345)

trainImg = tk.Button(window, text="TRAIN", fg="white", command=TrainImages, bg="deepskyblue",
                     width=15, height=2, activebackground="white", font=('kollektif', 15, ' bold '))
trainImg.place(x=1530, y=490)

trackImg = tk.Button(window, text="TRACK", fg="white", command=TrackImages, bg="deepskyblue",
                     width=15, height=2, activebackground="white", font=('kollektif', 15, ' bold '))
trackImg.place(x=1530, y=635)

quitWindow = tk.Button(window, text="QUIT", command=window.destroy, fg="white", bg="Red1",
                       width=12, height=2, activebackground="white", font=('kollektif', 15, ' bold '))
quitWindow.place(x=1870, y=490)

window.mainloop()
