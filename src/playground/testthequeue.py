import sys
import time
import numpy as np
import random
import matplotlib.pyplot as plt
import queue
from scipy.io.wavfile import read as wavread
from scipy.signal import blackmanharris
from pysoundcard import *
from math import log
from sys import float_info
from collections import deque

#takes a numpy vector.
#i am not sure what is in the vector. Hmm. 

def get_frequency(in_data, RATE, chunk):
	# Take the fft and square each value
	
	
	
	windowed = in_data[:,0] * blackmanharris(len(in_data))
	data_after_fft = np.fft.rfft(windowed)
	
	# Find the peak and interpolate to get a more accurate peak
	i = np.argmax(abs(data_after_fft))
	
	# Convert to equivalent frequency
	thefreq= chunk * i / len(windowed)

	data_in_decibels = map (lambda x : - 30 if x<sys.float_info.min else 20* log(x) , data_after_fft)
	peak_intensity = max(data_in_decibels)

	return thefreq, peak_intensity


block_length = 2048

class DrawingBuffer:
	def __init__(self, bufferSize):
		#self.buffer = deque([-30]*bufferSize, maxlen=bufferSize)		
		self.bufferSize = bufferSize
		self.current = 0 
		plt.axis([0, bufferSize, 0, 200])
		plt.ion()
		plt.show()

	def newFrame(self, frequency, intensity): # for now do nothing with intensity
		self.current = (self.current + 1 ) % self.bufferSize
		plt.scatter(self.current, frequency)
		plt.draw()

class DrawingBuffer2:
	def __init__(self, bufferSize):
		self.buffer = deque([-30]*bufferSize, maxlen=bufferSize)		
		self.bufferSize = bufferSize
		self.current = 0 
		plt.axis([0, bufferSize, -30, 200])
		plt.ion()
		plt.show()

	def newFrame(self, frequency, intensity): # for now do nothing with intensity
		self.buffer.append(frequency)
		plt.rese
		plt.plot(list(self.buffer))
		plt.draw()
		
def make_callback_that_draws(drawing_object):
	def callback(in_data, frame_count, time_info, status):
		drawing_object.newFrame(*get_frequency(in_data, frame_count, block_length))
		return (in_data, continue_flag)
	return callback
	
	
def make_callback_that_puts_into_queue(queue):
	def callback(in_data, frame_count, time_info, status):
		frequency, intensity = get_frequency(in_data, frame_count, block_length)
		queue.put((frequency, intensity,time.time()))
		return (in_data, continue_flag)
	return callback
	
def callback(in_data, frame_count, time_info, status):
	print(get_frequency(in_data, frame_count, 2048))
	return (in_data, continue_flag)

queue_for_the_stream = queue.Queue()

s = Stream(sample_rate=44100, block_length=block_length,output_device=False, callback=make_callback_that_puts_into_queue(queue_for_the_stream))

s.start()


while True:
	t = time.time()
	while(time.time()-t < 5.0):
		print((lambda x, y,z : (x,y,time.time()-z) )(*queue_for_the_stream.get()))
	time.sleep(10.0)
	
time.sleep(1000)
s.stop()








