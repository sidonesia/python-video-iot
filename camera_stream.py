
from flask          import Flask
from flask          import Response
from flask          import render_template
from imutils.video  import VideoStream

import cv2
import imutils
import time
import threading

outputFrame = None
lock = threading.Lock()
app  = Flask(__name__) 

vs = VideoStream(src=0).start()
time.sleep(2.0)

@app.route("/")
def index():
    return render_template("index.html")

def read_stream(frameCount):
    global vs, outputFrame, lock

    while True:
        frame = vs.read()
        frame = imutils.resize(frame, width=500, height=400)

        with lock:
            outputFrame = frame.copy()

def generate():
    global outputFrame, lock
    while True:
        with lock:
            if outputFrame is None:
                continue
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            if not flag:
                continue

        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype = "multipart/x-mixed-replace; boundary=frame")

if __name__ == '__main__':

    t= threading.Thread(target=read_stream, args=(
        1,))
    t.daemon = True
    t.start()

    app.run(host="0.0.0.0", port="8090", debug=True,
            threaded=True,use_reloader=False)
    

vs.stop()
