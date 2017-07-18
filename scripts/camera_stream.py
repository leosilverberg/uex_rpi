#!/usr/bin/env python

import sys
import io
import os
import shutil
from subprocess import Popen, PIPE
from string import Template
from struct import Struct
from threading import Thread
from time import sleep, time
from wsgiref.simple_server import make_server
from fractions import Fraction

from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor

import time
from datetime import datetime
import atexit
import curses

import picamera
from ws4py.websocket import WebSocket
from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication

###########################################
# CONFIG
WIDTH = 1024
HEIGHT = 768
FRAMERATE = 24
HTTP_PORT = 8082
WS_PORT = 8084
COLOR = u'#444'
BGCOLOR = u'#333'
JSMPEG_MAGIC = b'jsmp'
JSMPEG_HEADER = Struct('>4sHH')
mh = Adafruit_MotorHAT()
#setting up stepper1 200 steps/rev
decStepper = mh.getStepper(200,1)
raStepper = mh.getStepper(200,2)
decStepper.setSpeed(10)
raStepper.setSpeed(10)

broadcast_thread = None
websocket_server = None
output = None
camera = picamera.PiCamera()
camera.resolution = (2592,1944)
u_res = (1024,768)
camera.framerate = FRAMERATE
camera.annotate_text = str(camera.resolution)
camera.vflip = True
camera.shutter_speed = 0
###########################################
def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

def startBc():
	global websocket_server
	global output
	global camera
	global broadcast_thread
    
	output = BroadcastOutput(camera)
	broadcast_thread = BroadcastThread(output.converter, websocket_server)
	# print('Starting recording')
	camera.start_recording(output, 'yuv', resize=(1024,768))
	# print('Starting bc|||||||||||||##########')
	broadcast_thread.start()

class StreamingWebSocket(WebSocket):
    def opened(self):
        self.send(JSMPEG_HEADER.pack(JSMPEG_MAGIC, WIDTH, HEIGHT), binary=True)

class BroadcastOutput(object):
    def __init__(self, camera):
        # print('Spawning background conversion process')
        self.converter = Popen([
            'avconv',
            '-f', 'rawvideo',
            '-pix_fmt', 'yuv420p',
            '-s', '%dx%d' % u_res,
            '-r', str(float(camera.framerate)),
            '-i', '-',
            '-f', 'mpeg1video',
            '-b', '800k',
            '-r', str(float(camera.framerate)),
            '-'],
            stdin=PIPE, stdout=PIPE, stderr=io.open(os.devnull, 'wb'),
            shell=False, close_fds=True)

    def write(self, b):
        self.converter.stdin.write(b)

    def flush(self):
        # print('Waiting for background conversion process to exit')
        self.converter.stdin.close()
        self.converter.wait()
        
class BroadcastThread(Thread):
    def __init__(self, converter, websocket_server):
        super(BroadcastThread, self).__init__()
        self.converter = converter
        self.websocket_server = websocket_server

    def run(self):
        try:
            while True:
                buf = self.converter.stdout.read(512)
                if buf:
                    self.websocket_server.manager.broadcast(buf, binary=True)
                elif self.converter.poll() is not None:
                    break
        finally:
            self.converter.stdout.close()





class ControlThread(Thread):
	def __init__(self):
		super(ControlThread, self).__init__()
	
	def run(self):
		global websocket_server
		global output
		global camera
		global broadcast_thread
		while True:
			data = sys.stdin.readline()
			if data > "" :
				dataString = "str(data)"
				# print("[web->py]"+data)
				if dataString == "up\n" :
					print("[py] got up")
					raStepper.step(1,Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.MICROSTEP)
				elif dataString == "down\n" :
					print("[py] got down")
					raStepper.step(1,Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.MICROSTEP)
				elif dataString == "left\n" :
					print("[py] got left")
					decStepper.step(1,Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.MICROSTEP)
				elif dataString == "right\n" :
					print("[py] got right")
					decStepper.step(1,Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.MICROSTEP)
				elif dataString == "kill\n" :
					print("stop all processes")
				elif data["command"]["type"] == "move":
					print('{"msg":"mooves"}')
				elif dataString == "capture\n" :
					print("[py] capturing")
					try:
					
						print("[py] taking picture")
						
						camera.annotate_text = str(camera.resolution)
						print("[py] annotated")
						camera.stop_recording()
						print("[py] stopped rec")
						
						camera.resolution = (2592,1944)
						print("[py] changed to hi-res")
						camera.capture('captured/'+str(datetime.now())+'_uex1.jpg',format='jpeg', use_video_port=False, quality=100, bayer=True)
						print("[py]defualt picture taken")
						camera.framerate = (Fraction(1,6))
						camera.shutter_speed = 5000000
						camera.iso = 800
						sleep(10)
						camera.exposure_mode = 'off'
						print(camera.shutter_speed)
						
						camera.capture('captured/'+str(datetime.now())+'_long_exp_uex1.jpg',format='jpeg', use_video_port=False, quality=100, bayer=True)
						
						print("[py]long exp picture taken")
						
						camera.framerate = 24
						camera.shutter_speed = 0
						camera.iso = 100
						camera.exposure_mode='auto'
						sleep(20)
						
						startBc()
						print("[py] started broadcast again")
						
					except:
						pass
					#decStepper.step(1,Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.MICROSTEP)
					#with picamera.PiCamera() as camera:
					#picamera.PiCamera().stop_recording()
					#control_thread = ControlThread()
					#control_thread.start()
					#	camera.capture('test.jpg')


    
    		          
            
def main():
    print('{"msg":"Initializing camera"}')
    global websocket_server
    global output
    global camera
    global broadcast_thread
    
    #camera.resolution = (WIDTH, HEIGHT)
    #camera.framerate = FRAMERATE
    sleep(1) # camera warm-up time
    # print('Initializing websockets server on port %d' % WS_PORT)
    websocket_server = make_server(
		'', WS_PORT,
		server_class=WSGIServer,
		handler_class=WebSocketWSGIRequestHandler,
		app=WebSocketWSGIApplication(handler_cls=StreamingWebSocket))
    websocket_server.initialize_websockets_manager()
    websocket_thread = Thread(target=websocket_server.serve_forever)
    # print('Initializing broadcast thread')
    output = BroadcastOutput(camera)
    broadcast_thread = BroadcastThread(output.converter, websocket_server)
    # print('Starting recording')
    camera.start_recording(output, 'yuv', resize=(1024,768))
    # print('Starting motor inits & init control thread')
    atexit.register(turnOffMotors)
    control_thread = ControlThread()
    try:
        # print('Starting websockets thread')
        websocket_thread.start()
        # print('Starting broadcast thread')
        broadcast_thread.start()
        # print('Starting control thread')
        control_thread.start()
        while True:
            camera.wait_recording(1)
    except KeyboardInterrupt:
        pass
    finally:
        # print('Stopping recording')
        camera.stop_recording()
        # print('Waiting for broadcast thread to finish')
        broadcast_thread.join()
        # print('Shutting down websockets server')
        websocket_server.shutdown()
        # print('Waiting for websockets thread to finish')
        websocket_thread.join()


if __name__ == '__main__':
    main()
