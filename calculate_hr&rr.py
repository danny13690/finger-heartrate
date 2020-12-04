import pyedflib as bdf
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import heartpy as hp
import csv
import cv2

import datetime

from biosppy.signals.resp import resp as biosppy_resp
import biosppy
from scipy.signal import detrend, find_peaks, periodogram

EXT = ".MOV"
SESSION = "10_slow.MOV"
BASE_FREQUENCY = 60
NUM_SECONDS_IN_MINUTE = 60
NUM_BREATHS = 10

def plot(data):
	x = list(range(0, len(data)))
	plt.close('all')
	plt.figure(figsize=(32, 6))
	plt.plot(x, data, 'r-')
	plt.show()
	plt.close()

def save_plot(data, save_path, framerate, x_label='', y_label=''):
	x = list(range(0, len(data)))
	plt.close('all')
	plt.figure(figsize=(32, 6))
	plt.plot(x, data, 'r-')
	plt.title(save_path)
	plt.xlabel(x_label)
	plt.ylabel(y_label)
	plt.savefig(save_path)
	plt.close()

def process_ecg(data, show=False, framerate=BASE_FREQUENCY):
	filtered = hp.filter_signal(data, [0.7, 3.5], sample_rate=framerate, 
							order=3, filtertype='bandpass')
	#filtered = hp.remove_baseline_wander(filtered, FREQUENCY)
	wd, m = hp.process(hp.scale_data(filtered), framerate)
	if show:
		print(wd.keys())
		print(m.keys())
		hp.plotter(wd, m)

	save_plot(wd["breathing_signal"], 
			  str(framerate)+"breathing_signal_hp.png", 
			  framerate,
			  x_label='Time ('+str(framerate)+'hz)', 
			  y_label='Breathing Signal')

	hr = m["bpm"]
	rr = m["breathingrate"]
	RR_list = wd["RR_list"]

	return hr,rr, RR_list

def github_breathing(HRV,framerate):
	hr = framerate * (NUM_SECONDS_IN_MINUTE/HRV)
	edr = detrend(hr)
	edr = (edr - edr.mean()) / edr.std()
	resp_peaks, _ = find_peaks(edr, height=0)
	freqs, psd = periodogram(edr)
	return freqs[np.argmax(psd)]

def biosppy_bvp(signal):
	ts, filtered, onsets, hr_list_ts, hr_list = biosppy.signals.bvp.bvp(signal, FREQUENCY, False)

def main(argv):
	if len(argv) == 0:
		framerates = [60, 30, 20, 15, 10, 5]
	else:
		framerates = [argv[0]]

	with open('results.csv', 'w', newline='') as f:
		w = csv.writer(f)
		w.writerow(['Framerate',
					'HeartPy HR',
					'HeartPy Breaths Counted',
					'HeartPy Breathing Rate',
					'Github Breaths Counted',
					'Github Breathing Rate'])
		frequency = BASE_FREQUENCY
		signal = []
		cap = cv2.VideoCapture(SESSION)
		factor = BASE_FREQUENCY / framerate
		i = 0
		while(cap.isOpened()):
			ret, frame = cap.read()
			if not ret:
				break
			if i % factor == 0:
				signal.append(np.mean(np.array(frame)))
			i += 1
		cap.release()

		save_plot(signal, str(framerate) + "_raw_signal.png", framerate,
				  x_label='Time ('+str(framerate)+'hz)', y_label='BVP Signal')
		hr, rr, HRV = process_ecg(signal, False, framerate)
		github_rr = github_breathing(HRV, framerate)
		length = len(signal) / framerate
		gt_rr = NUM_SECONDS_IN_MINUTE * NUM_BREATHS / length
		w.writerow([framerate, hr, rr*length, rr*NUM_SECONDS_IN_MINUTE, github_rr*length, github_rr*NUM_SECONDS_IN_MINUTE])


if __name__ == "__main__":
	main(sys.argv[1:])