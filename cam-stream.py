import cv2
import signal, sys, os
from flask import Flask, render_template, Response
from argparse import ArgumentParser

# Get arguments from command line
parser = ArgumentParser()
parser.add_argument('--host', help="Host IP address", default=(os.environ["IP_LOCAL"] or '127.0.0.1'))
parser.add_argument('--input', help="Camera device file", default='/dev/video0')
parser.add_argument('--width', type=int, help="Horizontal video resolution (in pixel)", default=640)
parser.add_argument('--height', type=int, help="Vertical video resolution (in pixel)", default=480)
parser.add_argument('--run')
args = parser.parse_args()

ip_addr         = args.host
input_file      = args.input
frame_width     = args.width
frame_height    = args.height

print('[DEBUG] ip_addr =', ip_addr)
print('[DEBUG] input_file =', input_file)
print('[DEBUG] frame_width =', frame_width)
print('[DEBUG] frame_height =', frame_height)

# Initialize Camera
cam = cv2.VideoCapture(2)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

app = Flask(__name__)

# Get frames if camera is opened
def stream():
    while True:
        ret, frame = cam.read()
        if ret:
            imgencode = cv2.imencode('.jpg', frame)[1]
            string_data = imgencode.tostring()
            yield (b'--frame\r\n'b'Content-Type: text/plain\r\n\r\n'+string_data+b'\r\n')
        else:
            break

    cam.release()
    print('[LOG] Camera is closed!')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/live')
def live():
    return Response(stream(),mimetype='multipart/x-mixed-replace; boundary=frame')

# Handle SIGINT to make sure all resources are released before app exits
# def signal_handler(sig, frame):
#     print('[SIGINT] Closing... ')
#     cam.release()
#     sys.exit(0)
# signal.signal(signal.SIGINT, signal_handler)


# Run application 
if __name__ == '__main__':
    app.run(host=ip_addr, debug=True) 
