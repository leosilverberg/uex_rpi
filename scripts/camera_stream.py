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
import json

from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor

import time
from datetime import datetime, timedelta
import atexit
import curses

import picamera
from ws4py.websocket import WebSocket
from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication

from PIL import Image



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

EXPOSURE_TIME = 1
WHITE_BALANCE = "off"
ISO = 100

DEC_NUM_STEPS = 1
ALT_NUM_STEPS = 1
FOCUS_NUM_STEPS = 1

DEC_STEP_TYPE = "micro"
ALT_STEP_TYPE = "micro"
FOCUS_STEP_TYPE = "micro"
thumbnail_size = (200,200)
latest_image =""

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
		global EXPOSURE_TIME
		global WHITE_BALANCE
		global ISO

		global DEC_NUM_STEPS
		global ALT_NUM_STEPS
		global FOCUS_NUM_STEPS

		global DEC_STEP_TYPE
		global ALT_STEP_TYPE
		global FOCUS_STEP_TYPE
		global latest_image

		while True:
			data = sys.stdin.readline()
			if data > "" :
				dataString = "str(data)"
				print('{"msg":"got a data thing"}')
				decoded = json.loads(data)
				# print(data)
				if decoded["type"] == "move":
					print('{"msg":"###move###"}')
					if decoded["var"] == "dec":
						if decoded["val"] == "up":
							if DEC_STEP_TYPE == "micro":
								print('{"msg":"microstep"}')
								raStepper.step(int(DEC_NUM_STEPS),Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.MICROSTEP)
							elif DEC_STEP_TYPE == "single":
								print('{"msg":"singlestep"}')
								raStepper.step(int(DEC_NUM_STEPS),Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.SINGLE)
							elif DEC_STEP_TYPE == "double":
								print('{"msg":"doublestep"}')
								raStepper.step(int(DEC_NUM_STEPS),Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.DOUBLE)
							elif DEC_STEP_TYPE == "inter":
								print('{"msg":"interleaved step"}')
								raStepper.step(int(DEC_NUM_STEPS),Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.INTERLEAVE)
						elif decoded["val"] == "down":
							if DEC_STEP_TYPE == "micro":
								raStepper.step(int(DEC_NUM_STEPS),Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.MICROSTEP)
							elif DEC_STEP_TYPE == "single":
								raStepper.step(int(DEC_NUM_STEPS),Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.SINGLE)
							elif DEC_STEP_TYPE == "double":
								raStepper.step(int(DEC_NUM_STEPS),Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.DOUBLE)
							elif DEC_STEP_TYPE == "inter":
								raStepper.step(int(DEC_NUM_STEPS),Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.INTERLEAVE)
					elif decoded["var"] == "alt":
						if decoded["val"] == "left":
							if ALT_STEP_TYPE == "micro":
								decStepper.step(int(ALT_NUM_STEPS),Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.MICROSTEP)
							elif ALT_STEP_TYPE == "single":
								decStepper.step(int(ALT_NUM_STEPS),Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.SINGLE)
							elif ALT_STEP_TYPE == "double":
								decStepper.step(int(ALT_NUM_STEPS),Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.DOUBLE)
							elif ALT_STEP_TYPE == "inter":
								decStepper.step(int(ALT_NUM_STEPS),Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.INTERLEAVE)
						elif decoded["val"] == "right":
							if ALT_STEP_TYPE == "micro":
								decStepper.step(int(ALT_NUM_STEPS),Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.MICROSTEP)
							elif ALT_STEP_TYPE == "single":
								decStepper.step(int(ALT_NUM_STEPS),Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.SINGLE)
							elif ALT_STEP_TYPE == "double":
								decStepper.step(int(ALT_NUM_STEPS),Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.DOUBLE)
							elif ALT_STEP_TYPE == "inter":
								decStepper.step(int(ALT_NUM_STEPS),Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.INTERLEAVE)
				elif decoded["type"] == "settings":
					
					EXPOSURE_TIME = decoded["exposure"]
					

					WHITE_BALANCE = decoded["wb"]
					ISO = decoded["ISO"]

					DEC_NUM_STEPS = decoded["dec_num_steps"]
					ALT_NUM_STEPS = decoded["alt_num_steps"]
					FOCUS_NUM_STEPS = decoded["focus_num_steps"]

					DEC_STEP_TYPE = decoded["dec_step_type"]
					ALT_STEP_TYPE = decoded["alt_step_type"]
					FOCUS_STEP_TYPE = decoded["focus_step_type"]
					camera.awb_mode = str(WHITE_BALANCE)
					if WHITE_BALANCE == "off" :
						camera.awb_gains = float(decoded["wb_gains"])
					
					print('{"msg":"###UEX SETTINGS####"}')
					print('{"msg":"'+EXPOSURE_TIME+'"}')
					   
				elif decoded["type"] == "capture":
					print('{"msg":"###CAPTURE###"}')
					try:
						camera.stop_recording()
						print('{"msg":"stopped recording"}')
						camera.resolution = (2592,1944)
						print('{"msg":"set to high-res"}')
						camera.exposure_mode = 'off'
						camera.framerate = 1
						print('{"msg":"changed framerate"}')
						print('{"msg":"changing exposure"}')

						try:
							EXPOSURE_TIME = float(EXPOSURE_TIME)
							print('{"msg":"floated exposure"}')
							
						except ValueError:
							print('{"msg":"value error"}')
						except:
							print('{"msg":"some error occured in floating ========================"}')

						try:
							print('{"msg":"'+str(EXPOSURE_TIME)+'"}')
						except ValueError:
							print('{"msg":"value error in printing"}')
						except:
							print('{"msg":"some error occured in printing ========================"}')

						try:
							camera.shutter_speed = int(EXPOSURE_TIME*1000000)
							# camera.shutter_speed = 0
						except ValueError:
							print('{"msg":"value error"}')
						except TypeError:
							print('{"msg":"type error"}')
						except:
							print('{"msg":"some error occured in setting the shutterspeed========================"}')

						print('{"msg":"exposure speed:'+str(timedelta(microseconds=camera.exposure_speed))+'"}')

						
						print('{"msg":"changed exposure"}')
						camera.iso = int(ISO)
						print('{"msg":"changed ISO"}')
						sleep(5)
						camera.exposure_mode = 'off'
						print('{"msg":"taking photo"}')
						start_time = time.time()
						datestamp = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
						latest_image = 'captured/full_'+datestamp+'.jpg'
						camera.capture(latest_image,format='jpeg', use_video_port=False, quality=100, bayer=True)
						print('{"msg":"making thumbnail"}')
						try:
							tbn = 'captured/thumb_'+datestamp+'.jpg'
							im = Image.open(latest_image)
							im.thumbnail((200,200), Image.ANTIALIAS)
							im.save(tbn, 'JPEG')
							print('{"msg":"made thumbnail"}')
							print('{"img":"'+datestamp+'"}')
						except IOError:
							print('{"msg":"couldnt make thumbnail"}')
						elapsed_time = time.time() - start_time
						print('{"msg":"picture taken: '+str(elapsed_time)+' seconds"}')
						camera.framerate = 24
						camera.shutter_speed = 0
						camera.iso = 100
						camera.exposure_mode='auto'
						sleep(5)
						startBc()
						print('{"msg":"started bc"}')
						
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
