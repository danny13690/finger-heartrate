import matplotlib.pyplot as plt
import heartpy as hp
import numpy as np

from scipy.signal import resample

"""
Class: HeartRateHelper

Takes 1D data and returns appropriate data.

"""
class HeartRateHelper:
	def __init__(self, framerate, filter=True, resample=-1, show=False, save_path=''):
		self.show = show
		self.filter = filter
		self.framerate = framerate
		self.resample = resample

		# if save_path is empty, do not save
		self.save_path = save_path

		# saves the last calculated m, wd
		self.m = None
		self.wd = None

	def save_plot(self, data, x_label='', y_label=''):
		x = list(range(0, len(data)))
		plt.close('all')
		plt.figure(figsize=(32, 6))
		plt.plot(x, data, 'r-')
		plt.title(self.save_path)
		plt.xlabel(x_label)
		plt.ylabel(y_label)
		plt.savefig(self.save_path)
		plt.close()

	def get_heartrate_and_breathing(self, data):
		framerate = self.framerate
		if self.resample != -1:
			data = resample(data, (len(data)//self.framerate)*self.resample)
			framerate = self.resample

		if self.filter:
			data = hp.filter_signal(data, [0.7, 3.5], sample_rate=framerate, 
							order=3, filtertype='bandpass')
			data = hp.scale_data(data)

		wd, m = hp.process(data, framerate, high_precision = True, clean_rr = True)

		self.m = m
		self.wd = wd
		hr = m["bpm"]
		rr = m["breathingrate"]

		if self.show:
			hp.plotter(wd, m)

		if self.save_path != '':
			save_plot(data, x_label="Time", y_label="BVP Signal")

		return hr, rr * 60