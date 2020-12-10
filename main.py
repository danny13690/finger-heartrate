import os
import sys
import datetime

import numpy as np
import csv
import cv2

from heartratehelper import HeartRateHelper

EXT = ".MOV"
SESSION = "10_slow.MOV"
BASE_FREQUENCY = 60
NUM_SECONDS_IN_MINUTE = 60
NUM_BREATHS = 10

def main(argv):
	signal = []

	cap = cv2.VideoCapture(SESSION)
	while(cap.isOpened()):
		ret, frame = cap.read()
		if not ret:
			break
		signal.append(np.mean(np.array(frame)))
	cap.release()

	helper = HeartRateHelper(BASE_FREQUENCY, filter=True, resample=-1, show=True, save_path='')
	hr, rr = helper.get_heartrate_and_breathing(signal)

if __name__ == "__main__":
	main(sys.argv[1:])