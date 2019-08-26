#!/usr/bin/python3

from ramper import *
import time
import logging
import sys
import json
import exceptions as ex


class KilnOperationServer:
    '''to be launched to control kiln via web'''

    def __init__(self, name="UNNAMED_KILN",
                 cmd_bank_path="/home/chanceygardener/KilnCommands.json",
                 test_env_params=None):
        initime = time.time()
        self.log = {'init_time': initime}
        if test_env_params is None:
            # TODO(chanceygardener): this will be sensor 
            	# read data outside of certain tests
            raise NotImplemented
        else:
            self.env = EnvModel(kwargs=test_env_params)
        self.__name__ = name
        self.lock_active = False  # set true while FiringPlan is Active.
        # configure command interface
        try:
            with open(cmd_bank) as cbank:
                self.cmd_bank = json.loads(cbank.read())
        except:  # TODO: figure out what the JSOn parse error is
            logging.error("\nCould not parse json at {}".format(cmd_bank_path))
            sys.exit()

    def __str__(self):
        active_status = """active at stage: {}
		 ramp: {} degrees {} per hour
		  target temperature: {}""" if self.lock_active else ""
        return self.__name__ + active_status

    def _requestLock(self):
        if self.lock_active:
            raise ex.KilnInUseError(self)

    def _getCommand(self, source):
        if source == 'stdin':
            return input("enter command: ")
        else:
            raise NotImplemented  # device input not yet implemented

    def _run(self):
        cmd = 'INIT'
        while cmd != 'EXIT':
            try:
                instruct = self.cmd_bank[cmd]
            except KeyError:
                logging.error("\nunknown command: {}".format(cmd))

            cmd = self._getCommand('stdin')


if __name__ == "__main__":
    with open('test_env_values.json') as jfile:
        test_params = json.loads(jfile.read())
    kiln = KilnOperationServer(name="TEST_KILN", test)
