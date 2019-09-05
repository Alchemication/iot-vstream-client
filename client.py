# import the necessary packages
from imutils.video import VideoStream
from imutils import resize
from imagezmq import imagezmq
import argparse
import socket
import time
import sys
import cv2
import traceback

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", required=True,
    help="ip address of the server to which the client will connect")
ap.add_argument("-p", "--server-port", required=False, default=5555,
    help="port of the server to which the client will connect")
ap.add_argument("-f", "--flip-image", required=False, default='N',
    help="do we want to flip the image by 180 degrees")
ap.add_argument("-w", "--res-width", required=False, default=1920,
    help="resolution width")
ap.add_argument("-e", "--res-height", required=False, default=1088,
    help="resolution height")
ap.add_argument("-c", "--jpg-compression", required=False, default=90,
    help="jpg compression, lower = lower network latency")
args = vars(ap.parse_args())

# get the host name of the machine
rpi_name = socket.gethostname()

# initialize the ImageSender object with the socket address of the server
zmq_url = 'tcp://{}:{}'.format(args["server_ip"], args["server_port"])
print('[INFO] Connecting {} to imagezmq server on {}...'.format(rpi_name, zmq_url))
sender = imagezmq.ImageSender(connect_to=zmq_url)

# initialize the video stream, and allow the
# camera sensor to warmup
print('[INFO] Warming up camera sensor...')
res_dim = (int(args['res_width']), int(args['res_height']))
vs = VideoStream(usePiCamera=True, resolution=res_dim).start()
time.sleep(2.0)

# start streaming images
print('[INFO] Streaming video at resolution: {}...'.format(res_dim))
try:
    while True: # send images as stream until Ctrl-C

        # read the frame from the camera
        frame = vs.read()

        # check if image needs to be flipped
        if args['flip_image'].upper() != 'N':
            frame = cv2.rotate(frame, rotateCode=cv2.ROTATE_180)

        # encode as jpg
        ret_code, jpg_buffer = cv2.imencode(
            ".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), args['jpg_compression']])
        
        # send to the message queue server
        sender.send_jpg(rpi_name, jpg_buffer)

except (KeyboardInterrupt, SystemExit):
    pass  # Ctrl-C was pressed to end program
except Exception as ex:
    print('[ERR] Python error with no Exception handler:')
    print('[ERR] Traceback error:', ex)
    traceback.print_exc()
finally:
    vs.stop()
    sys.exit()