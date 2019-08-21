#!/usr/bin/python3

import time
import RPi.GPIO as GPIO

FULL_PULSE_IN_SECONDS = 3

class PulseWidthModulator:
	def __init__(self, output):
		self._active_time = 0
		self._full_pulse = FULL_PULSE_IN_SECONDS
		self._output = output

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

