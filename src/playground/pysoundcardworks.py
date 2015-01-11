import sys
import time
import numpy as np
import random
import matplotlib.pyplot as plt
from scipy.io.wavfile import read as wavread
from scipy.signal import blackmanharris
from pysoundcard import *
from math import log
from sys import float_info

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

if __name__ == '__main__':
	block_length = 2048
	
	def callback(in_data, frame_count, time_info, status):
		print(get_frequency(in_data, frame_count, 2048))
		return (in_data, continue_flag)

	
	s = Stream(sample_rate=44100, block_length=block_length,output_device=False, callback=callback)
	s.start()
	time.sleep(1000)
	s.stop()