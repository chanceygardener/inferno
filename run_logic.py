#!/usr/bin/python3

from ramper import *
import time
import logging
import sys




class KilnOperationServer:
	'''to be launched to control kiln via web'''
	def __init__self(cmd_bank_path="/home/chanceygardener/KilnCommands.json"):
		initime = time.time()
		self.log = {'init_time':initime}
		self.env = EnvModel(**kwargs)
		try:
			with open(cmd_bank) as cbank:
				self.cmd_bank = json.loads(cbank.read())
		except: #TODO: figure out what the JSOn parse error is 
			logging.error("\nCould not parse json at {}".format(cmd_bank_path))
			sys.exit()
	def _getCommand(self, source):
		if source == 'stdin':
			return input("enter command: ")
		else:
			return 'NULL' # device input not yet implemented

	def _run(self):
		cmd = 'INIT'
		while cmd != 'EXIT':
			try:
				instruct = self.cmd_bank[cmd]
			except KeyError:
				logging.error("\nunknown command: {}".format(cmd))
			
			cmd = self._getCommand('stdin')





