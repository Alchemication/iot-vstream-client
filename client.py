# import the necessary packages
from imutils.video import VideoStream
from imutils import resize
from imagezmq import imagezmq
import argparse
import socket
import time

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
print('[INFO] Streaming video at res width {}...'.format(res_dim))
while True:
    # read the frame from the camera and send it to the server
    frame = vs.read()
    frame = resize(frame, width=res_dim[0], height=res_dim[0])
    sender.send_image(rpi_name, frame)
    time.sleep(0.1)
