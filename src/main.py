import sys
import time
import numpy as np
import random
import matplotlib.pyplot as plt
import queue
import matplotlib.animation as animation
import threading
from scipy.io.wavfile import read as wavread
from scipy.signal import blackmanharris
from pysoundcard import *
from math import log
from sys import float_info
from collections import deque

"""
This function takes a numpy vector that represents the sampled sound from the stream, and processes it. 
"""
def get_frequency(in_data, chunk):
	# Take the fft and square each value
	
	windowed = in_data[:,0] * blackmanharris(len(in_data))
	data_after_fft = np.fft.rfft(windowed)

	# Find the peak
	i = np.argmax(abs(data_after_fft))
	
	# Convert to equivalent frequency
	# TODO: calibrate the frequency so it shows up in Hz ,this is not the right calculation
	thefreq= chunk * i / len(windowed)

	data_in_decibels = map (lambda x : - 30 if x<sys.float_info.min else 20* log(x) , data_after_fft)
	# TODO: a more accurate method would be to use quadratic interpolation around this value to get a better estimate of where the maximum is
	# TODO: the code iterates through the chunk again needlessly to find the peak intensity. Improve the algorithm. 
	peak_intensity = max(data_in_decibels)

	return thefreq, peak_intensity

"""
The API for the sound input operates on callbacks. A function like this needs to be provided to the constructor: 

def simple_callback(in_data, frame_count, time_info, status):
	print(get_frequency(in_data, frame_count, 2048))
	return (in_data, continue_flag)	
	
which is then called asynchronously after the chunk of input is received. 
	
"""	


def make_callback_that_puts_into_queue(queue):
	def callback(in_data, frame_count, time_info, status):
		frequency, intensity = get_frequency(in_data, block_length)
		queue.put((frequency, intensity))
		return (in_data, continue_flag)
	return callback
	

queue_for_the_stream = queue.Queue()

# FFT works best when the block length is a power of two. 
block_length = 2048
s = Stream(sample_rate=44100, block_length=block_length,output_device=False, callback=make_callback_that_puts_into_queue(queue_for_the_stream))

s.start()
"""
The input part of the code finishes here. The input gets taken from the stream, transformed and placed into a queue.
We can retrieve the data with the queue.get() operation. The operation works very nicely, because if the queue is empty, it blocks until it can receive an input.
"""



"""
A simple implementation of a display.
We store the incoming data into a buffer. One thread fills the buffer constantly, the other redraws the buffer as fast as it can.

"""

buffer_size = 20
buffer = deque([0]*buffer_size, maxlen=buffer_size)
# let the thread add elements to the queue in a loop.

#TODO: think of a better implementation that doesn't involve a separate thread and time.sleep(). 
def keepFillingTheBuffer(queue,buffer):
	while True:
		time.sleep(0.03) # 0.03 is about half the time between successive chunks appearing.
		next , threshold = queue.get()
		buffer.append(next)


t= threading.Thread(target=keepFillingTheBuffer, args = (queue_for_the_stream, buffer))
t.daemon=True
t.start()
		

"""
This makes an animation using matplotlib. Shamelessly copypasted and slightly adapted.
"""		
fig = plt.figure()
ax = plt.axes(xlim=(0, 20), ylim=(10, 160))
line, = ax.plot([], [], lw=2)
def init():
	line.set_data([], [])
	return line,
def make_animate( buffer, queue):
	def animate(i):
		x = np.linspace(0, buffer_size, buffer_size)
		y = list(buffer)
		line.set_data(x, y)
		return line,
	return animate
animate = make_animate(buffer, queue_for_the_stream)
# call the animator.  blit=True means only re-draw the parts that have changed.
anim = animation.FuncAnimation(fig, animate, init_func=init, blit=True)

plt.show()	

#TODO: implement stopping after a keystroke as opposed to ctrl+c. 
time.sleep(1000)
s.stop()




"""
I experimented with the callback function that takes an object responsible for plotting.
The problem was that the plotting might be slower than incoming data, so you can't redraw every time you receive a chunk. 
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

def make_callback_that_draws(drawing_object):
	def callback(in_data, frame_count, time_info, status):
		drawing_object.newFrame(*get_frequency(in_data, frame_count, block_length))
		return (in_data, continue_flag)
	return callback
	
"""	


