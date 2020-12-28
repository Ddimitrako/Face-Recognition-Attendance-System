from flask import Flask, render_template, Response, request,redirect,url_for
import cv2
from AttedanceProject import VideoCamera
import requests
app = Flask(__name__)

#camera = cv2.VideoCapture('http://192.168.2.10:21866/videostream.cgi?user=admin&pwd=gigirivas',cv2.CAP_FFMPEG)
        
#camera = cv2.VideoCapture(0)  # use 0 for web camera
#for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
# for local webcam use cv2.VideoCapture(0)

app.route('/Download')
def download_file ():
    #For windows you need to use drive name [ex: F:/Example.pdf]
    path = "home/pi/Desktop/FaceRecognitionProject/Attendance.csv"
    return send_file(path, as_attachment=True)

def gen_frames():  # generate frame by frame from camera
    CameraObj = VideoCamera()
    while True:
            frame = CameraObj.FaceRecognition()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/buttonUP')
def up():
    Up=requests.get('http://192.168.2.2:29626/decoder_control.cgi?loginuse=admin&loginpas=gigirivas&onestep=1&command=0')  
    print("UP PRESSED")
    print(Up.status_code, Up.reason)
    return (''),204
@app.route('/buttonDOWN')
def down():
    Down=requests.get('http://192.168.2.2:29626/decoder_control.cgi?loginuse=admin&loginpas=gigirivas&onestep=1&command=2')
    print("DOWN PRESSED")
    print(Down.status_code, Down.reason)
    return (''),204
@app.route('/buttonLEFT')
def left():
    Left=requests.get('http://192.168.2.2:29626/decoder_control.cgi?loginuse=admin&loginpas=gigirivas&onestep=1&command=4')
    print("LEFT PRESSED")
    
    return (''),204
@app.route('/buttonRIGHT')
def right():
    Right=requests.get('http://192.168.2.2:29626/decoder_control.cgi?loginuse=admin&loginpas=gigirivas&onestep=1&command=6') 
    print("RIGHT PRESSED")
    
    return (''),204
# @app.route('/index',methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         if request.form['up'] == 'Do Something':
#             print("CAMERA LOOK UP ONE STEP")
#         elif request.form['down'] == 'Do Something Else':
#             print("CAMERA LOOK DOWN ONE STEP")
#         else:
#             pass  # unknown
#     elif request.method == 'GET':
#          print('get')
#     """Video streaming home page."""
    #return render_template('index.html')


# Route for handling the login page logic
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return render_template('index.html')
            #return redirect(url_for('index'))
    return render_template('login.html', error=error)

if __name__ == '__main__':

    app.run(host='0.0.0.0',port=5000,debug=True,threaded=True)