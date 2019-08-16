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
args = vars(ap.parse_args())
 
# initialize the ImageSender object with the socket address of the
# server
print('[INFO] Connecting to imagezmq server on tcp://{}:5555'.format(args["server_ip"]))
sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(
   args["server_ip"]))

print('[INFO] Warming up camera sensor...')
# get the host name, initialize the video stream, and allow the
# camera sensor to warmup
rpi_name = socket.gethostname()
vs = VideoStream(usePiCamera=True).start()
#vs = VideoStream(src=0).start()
time.sleep(1.0)

res_dim = (400, 400)
jpeg_quality = 95
print('[INFO] Streaming video...')
try:
    while True: # send images as stream until Ctrl-C

        # read the frame from the camera
        frame = vs.read()

        # resize image
        frame = resize(frame, width=res_dim[0], height=res_dim[0])

        # encode as jpg
        ret_code, jpg_buffer = cv2.imencode(
            ".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
        sender.send_jpg(rpi_name, jpg_buffer)

        # keep sleep for testing, but change to 0.0 in prod
        #time.sleep(2.0)
        time.sleep(0.0)
except (KeyboardInterrupt, SystemExit):
    pass  # Ctrl-C was pressed to end program
except Exception as ex:
    print('[ERR] Python error with no Exception handler:')
    print('[ERR] Traceback error:', ex)
    traceback.print_exc()
finally:
    vs.stop()
    sys.exit()