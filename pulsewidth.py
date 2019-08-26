#!/usr/bin/python3

import time
import RPi.GPIO as GPIO

FULL_PULSE_IN_SECONDS = 3

class TemperatureDelta:
	'''helper class to apass info t FIreplan'''
	def __init__(self, initial, final, time_frame=FULL_PULSE_IN_SECONDS):
		self.initial = initial
		self.final = final
		self.time_frame = time_frame

	def delta(self):
		return (self.final-self.initial) / self.time_frame


class PulseWidthModulator:
	def __init__(self, output):
		self._active_time = 0
		self._full_pulse = FULL_PULSE_IN_SECONDS
		self._output = output

	def get_active_time():
		return _active_time

	def set_active_time(self, time_in_seconds):
		self._active_time = time_in_seconds

	def add_active_time(self, time_in_seconds):
		self._active_time += time_in_seconds

	def reset_active_time(self, time_in_seconds):
		self._active_time = 0

	def _on(self):
		GPIO.output(self._output, GPIO.HIGH)

	def _off(self):
		GPIO.output(self._output, GPIO.LOW)

	def pulse(self):
		inactive_time = self._full_pulse - self._active_time
		self._on()
		time.sleep(self._active_time)
		self._off()
		time.sleep(inactive_time)

