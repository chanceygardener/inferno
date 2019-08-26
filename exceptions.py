#!/usr/bin/python3


 class KilnInUseError(Exception):
 	def __init__(self, host):
 		self.host = host
 	def __str__(self):
 		return "Kiln: '{}' Already in use by another firing program".format(self)



