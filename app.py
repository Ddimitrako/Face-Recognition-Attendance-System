from flask import Flask, render_template, Response, request,redirect,url_for,send_file
import cv2
from AttedanceProject import VideoCamera

app = Flask(__name__)

#camera = cv2.VideoCapture(0)  # use 0 for web camera
#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
# for local webcam use cv2.VideoCapture(0)


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
    print("UP PRESSED")
    return (''),204
@app.route('/buttonDOWN')
def down():
    print("DOWN PRESSED")
    return (''),204
@app.route('/buttonLEFT')
def left():
    print("LEFT PRESSED")
    return (''),204
@app.route('/buttonRIGHT')
def right():
    print("RIGHT PRESSED")
    return (''),204

@app.route('/button')
def picture():
    print("Picture Taken")
    return (''),204

@app.route('/return-file/')
def return_file():
    print("file downloaded")
    return send_file('C:\\Users\\ddimitrakopoulos\\Documents\\MEGA\\Python\\FaceRecognition-Streaming\\Face recognition V1\\FaceRecognitionProject V1\\Attendance.csv')


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

    app.run(debug=False,threaded=True)