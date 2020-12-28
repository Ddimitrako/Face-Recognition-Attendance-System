import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
from time import perf_counter
import time
from flask import Flask, render_template, Response, request
import requests
'''try:
    url='http://192.168.2.5:22500' 
    pass
    
    Up=requests.get('http://192.168.2.5:22500/decoder_control.cgi?loginuse=admin&loginpas=gigirivas&onestep=1&command=0')    
    time.sleep(2)
    Down=requests.get('http://192.168.2.5:22500/decoder_control.cgi?loginuse=admin&loginpas=gigirivas&onestep=1&command=2')
    time.sleep(2)
    Left=requests.get('http://192.168.2.5:22500/decoder_control.cgi?loginuse=admin&loginpas=gigirivas&onestep=1&command=4')
    time.sleep(2)
    Right=requests.get('http://192.168.2.5:22500/decoder_control.cgi?loginuse=admin&loginpas=gigirivas&onestep=1&command=6') 
    print(Up.status_code, Up.reason)
except:
    print('exception')
    pass
    '''
#path = 'C:/Users/ddimitrakopoulos/Documents/MEGA/Python/FaceRecognition-Streaming/Face recognition V1/FaceRecognitionProject V1/Images'
#path='C:/Users/dimitris/Documents/MEGA/Python/FaceRecognition-Streaming/Face recognition V1/FaceRecognitionProject V1/Images'
path = '/home/pi/Desktop/Tornado-mjpeg-streamer-python-master/Images' # path gia raspberry
images = []
classNames = []
myList = os.listdir(path)
print(myList)
global name
flags=[]
startTime=[]
stopTime=[]
for i in range(4):
    startTime.append(time.clock())
    stopTime.append(None)

faceTracking=True
for cl in myList:
    curImg = cv2.imread(f"{path}/{cl}")
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])  # print only name from name.jpg
print(classNames)
countImages = len(images)

def findEncodings(images):
    proccessingTimeSum = 0
    encodeList = []
    imageNum = 0
    global classNames
    for img, imageName in zip(images, classNames):
        currentTime = perf_counter()
        imageNum += 1
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # convert image to RGB
        encode = face_recognition.face_encodings(img)[0]  # find the encodings
        encodeList.append(encode)
        pastTime = perf_counter()
        proccessingTime = round(pastTime - currentTime, 2)
        proccessingTimeSum += proccessingTime
        print(f'Name: {imageName} Number {imageNum} of {countImages} Proccessing Time in Sec: {proccessingTime}')
        print('#####################################################################')
    print(f'proccessing Time Sum: {proccessingTimeSum}')
    return encodeList


def markAttendance(name):
    with open('Attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('Date:%D Time:%H:%M:%S')
            f.writelines(f'\n{name},{dtString}')
        elif name in nameList:
            print(f'{name} already in attendance list')


#### FOR CAPTURING SCREEN RATHER THAN WEBCAM
# def captureScreen(bbox=(300,300,690+300,530+300)):
#     capScr = np.array(ImageGrab.grab(bbox))
#     capScr = cv2.cvtColor(capScr, cv2.COLOR_RGB2BGR)
#     return capScr

encodeListKnown = findEncodings(images)
print(f'Number of known person: {len(encodeListKnown)}')
print('Encoding Complete')


# cap = cv2.VideoCapture(0)
class VideoCamera(object):
    def __init__(self):
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"
        #self.cap = cv2.VideoCapture('rtsp://admin:888888@192.168.2.5:10554/udp/av0_0',cv2.CAP_FFMPEG)
        self.cap = cv2.VideoCapture('http://192.168.2.10:21866/videostream.cgi?user=admin&pwd=gigirivas',cv2.CAP_FFMPEG)
        #self.cap = cv2.VideoCapture(0)
        time.sleep(2)
        # success, image = self.cap.read()

    def __del__(self):
        self.cap.release()

    def get_frame(self):
        success, img = self.cap.read()

    def FaceRecognition(self):
        success, img = self.cap.read()
        # img = captureScreen()

        imgSmall = cv2.resize(img, (0, 0), None, 0.25, 0.25)  # makes original image smaller by 75% for faster results
        imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgSmall)
        encodesCurFrame = face_recognition.face_encodings(imgSmall, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            print(faceDis)  # the lowest faceDis parameter is the face in the camera matched to the known face
            matchIndex = np.argmin(faceDis)

            if faceDis[matchIndex] < 0.55:
                name = classNames[matchIndex].upper()
                markAttendance(name)
                print(f'{name}: {faceDis[matchIndex]}')
                name = name.split()
                colorX = 0 #green Color
                colorY = 255
                colorZ = 0
            else: #red Color
                name = 'Unknown'
                print(name)
                colorX = 0
                colorY = 0
                colorZ = 255

            top, right, bottom, left = faceLoc

            top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4
            offset = 25
            cv2.rectangle(img, (left - offset, top - offset), (right + offset, bottom + offset),
                          (colorX, colorY, colorZ), 2)
            cv2.rectangle(img, (left - offset, bottom + offset), (right + offset, bottom), (colorX, colorY, colorZ),
                          cv2.FILLED)
        
            if name != 'Unknown':
                cv2.putText(img, name[0], (left - offset, bottom + offset - 25), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                            (255, 255, 255), 2)
                cv2.putText(img, name[1], (left - offset, bottom + offset), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                            (255, 255, 255), 2)
            elif name == 'Unknown':
                cv2.putText(img, name, (left - offset, bottom + offset - 25), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                            (255, 255, 255), 2)
                now = datetime.now()
                return_value, image = self.cap.read()
                cv2.imwrite(f'/home/pi/Desktop/Tornado-mjpeg-streamer-python-master/Unknown-Faces/{now}.jpg', image)
            if faceTracking:
                y=bottom + offset - 25
                x=left - offset
                print(f"bottom:{bottom} left{left} x: {x}  y:{y}")
                if x>360:
                    stopTime[0]=time.clock()
                    if stopTime[0] - startTime[0]>2:
                        Right=requests.get('http://192.168.2.2:29626/decoder_control.cgi?loginuse=admin&loginpas=gigirivas&onestep=1&command=6') 
                        startTime[0]=time.clock()
                       
                elif x<100:
                    stopTime[1]=time.clock()
                    if stopTime[1] - startTime[1]>2:
                        Left=requests.get('http://192.168.2.2:29626/decoder_control.cgi?loginuse=admin&loginpas=gigirivas&onestep=1&command=4')
                        startTime[1]=time.clock()
                    
                if y>330:
                    stopTime[2]=time.clock()
                    if stopTime[2] - startTime[2]>2:
                        Down=requests.get('http://192.168.2.2:29626/decoder_control.cgi?loginuse=admin&loginpas=gigirivas&onestep=1&command=2')
                        startTime[2]=time.clock()
                elif y<170:
                    stopTime[3]=time.clock()
                    if stopTime[3] - startTime[3]>2:
                        Up=requests.get('http://192.168.2.2:29626/decoder_control.cgi?loginuse=admin&loginpas=gigirivas&onestep=1&command=0')                           
                        startTime[3]=time.clock()
            
        cv2.imshow('Face Recognition', img)
        cv2.waitKey(1)  # 1: show video 0:show frame with a press o

        ret, jpeg = cv2.imencode('.jpg', img)
        return jpeg.tobytes()

    def FaceRecognitionLoop(self):
        while True:
            self.FaceRecognition()

'''obj=VideoCamera()
obj.FaceRecognitionLoop()'''