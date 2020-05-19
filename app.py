import os, cv2
from argparse import ArgumentParser
from flask import Flask, render_template, Response

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/live')
def live():
	return Response(get_video(),mimetype='multipart/x-mixed-replace; boundary=frame')

def init_cam(src='/dev/video0', width=640, height=480):
	global cam, device
	print('[LOG] Initializing camera', src)
	device = int(src) if src.isdigit() else src
	cam = cv2.VideoCapture(device)
	cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
	cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
#	print('[LOG] INFO:', cam.get(cv2.CAP_PROP_XI_DEVICE_MODEL_ID))

def get_video():
	while True:
		ret, frame = cam.read()
		if ret:
			imgencode = cv2.imencode('.jpg', frame)[1]
			string_data = imgencode.tostring()
			yield (b'--frame\r\n'b'Content-Type: text/plain\r\n\r\n'+string_data+b'\r\n')
		else:
			break
	cam.release()
	print('[ERROR] No access to camera', device)

if __name__ == '__main__':
	# Get arguments from command line
	parser = ArgumentParser()
	parser.add_argument('--host', help="Host IP address", default=(os.environ.get("IP_LOCAL", '127.0.0.1')))
	parser.add_argument('--device', help="Camera device file or index (e.g. /dev/video2 or 2)", default='/dev/video0')
	parser.add_argument('--width', type=int, help="Horizontal video resolution (in pixel)", default=640)
	parser.add_argument('--height', type=int, help="Vertical video resolution (in pixel)", default=480)
	args = parser.parse_args()

	# Initialize camera only inside child process if run in debug mode
	if os.environ.get('WERKZEUG_RUN_MAIN') or Flask.debug is False:
		init_cam(args.device, args.width, args.height)

	#print('[DEBUG:{}] starting flask app... '.format(os.getpid()))
	app.run(host=args.host, debug=True, use_reloader=True)


