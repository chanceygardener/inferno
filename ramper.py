#!/usr/bin/python3

import warnings
import ABC
import logging
import math
import json
import time
from max31855 import MAX31855 as tcdriver
from pulsewidth import PulseWidthModulator, FULL_PULSE_IN_SECONDS
from utils import GAS_CONST, RAMP_RATE_DENOMINTATION_IN_SECONDS

# Note: All times are in seconds unless otherwise noted.


SECONDS_IN_HOUR = 3600
SSR_PIN = 16  # not sure about that one yet


class KilnState(ABC):
	def __init__(self, host, name=None):
		self.host = host
		self.state_name = self._nameMe(state_name=name)
		self._buildLoggerAtHost()

	def _nameMe(self, state_name):
		raise NotImplemented

	def _buildLoggerAtHost(self):
		self.host[self.__name__] = logging.getLogger(self.__name__)


class EnvModel:
    '''A kiln element will lose efficacy as resistance increases with wear
     according to Power (joules) = voltage **2 / resistance '''

    def __init__(self, **kwargs):
        self.gas_const = GAS_CONST
        # warnings.warn("Environment model initiated with all 0 values")
        self.res = element_resistance  # resistance
        self.volt = voltage  # voltage
        self.log = {}

    def _heatInJoules(self):
        return self.volt**2 / self.res

    def _getHeatCapacity(self, t0, t1):
        self.heatInJoules() / (self.massofAir() * (t1-t0))

    def _massofAir(self):
        '''calculate the mass of the air given the pressure and temperature'''
        num = (self.atm_pres * self.env_vol)
        denom = (self.gas_const * self.molar_mass_air)
        return num / denom

    def _predictdDeltaTemp(self, initemp, degree_type='C'):
        raise NotImplemented

    def calculateNextPulseWidth(self, error):
        raise NotImplemented


class rampHoldStage:
    '''ramp hold stage holds segment of PLAN,
    which ENV inference methods try to fit'''

    def __init__(self, ramp_rate, unit, start_at, stop_at, hold_time, plan):
        self.ramp_rate = ramp_rate  # degree C per hour
        self.unit = unit
        self.stop_at = stop_at
        self.hold_time = hold_time
        self.plan = plan
        self.ideal_pulse_dt = self.ramp_rate /
        (self.plan.pwm._full_pulse * SECONDS_IN_HOUR)
        self._pulse_plan = self._planByPulse()
        self._pulses_in_stage = len(self._pulse_plan)

    def getPulseStartError(self, idx, actual_start):
        '''evaluates the error between the actual
        delta in temperature and the rampHoldStage's
        prescribed one
        param -- idx: index of pulse_plan to compare against
        actual -- temperature value read from thermocouple'''
        err = self._pulse_plan[idx][0] - actual_start
        return err

    def getPulseEndError(self, idx, actual_end):
        '''evaluates the error between the actual
        delta in temperature and the rampHoldStage's
        prescribed one
        param -- idx: index of pulse_plan to compare against
        actual -- temperature value read from thermocouple'''
        err = self._pulse_plan[idx][1] - actual_end
        return err

    def _planByPulse(self):
        pulse_plan = []
        hours = (self.stop_at - self.start_at) / self.ramp_rate
        pulse_count = math.ceil(
            hours * (SECONDS_IN_HOUR / self.plan.pwm._full_pulse))
        for p in range(len(pulse_count)):
            steps_from_stage_init = p * self.ideal_pulse_dt
            pulse_start = self.start_at + steps_from_stage_init
            temp_span = (pulse_start, pulse_start+self.ideal_pulse_dt)
            pulse_plan.append(temp_span)
        return pulse_plan


class IdleState(KilnState):
	def __init__(self, host, name=None):
		KilnState.__init__(self, host, state_name=name)


class FiringPlan(KilnState):
    def __init__(self, stages, temp_unit, host, program_name=None):
    	KilnState.__init__(self, host=host)
        self.host = host
        self.log = logging.getLogger()
        self.pwm = PulseWidthModulator(SSR_PIN)
        self.model = EnvModel()
        self.tc = tcdriver()
        self.temp_unit = temp_unit
        self.plan = []
        self.errlog = {}
        self.active = False
        stages_or_err = self._readStageData(stages)
        if isinstance(stages_or_err, json.decoder.JSONDecodeError):
            print("\nJSON firing plan data failed to parse, check error log\n")
            self.__exit__()
        else:
            self._compose(stages_or_err)
        self._nameMe(state_name=program_name)

    def _readStageData(self, stages):
        try:
            stage_dat = json.loads(stages)
        except json.decoder.JSONDecodeError as e:
            self.errlog['JSON_PARSE_ERR'] = e
            return e
        return stage_dat

    def getPlanTarget(self):
    	'''just returns the target temp'''
    	return self.plan[-1].stop_at

    def _nameMe(self, state_name=None):
    	if state_name is None:
        	self.__name__ = "{}-stage program -> {} degrees {}".format(len(self.plan),
        												self.getPlanTarget(),
        												self.temp_unit)
        else:
        	self.__name__ = state_name

    def _getRequiredPulseWidthForTempDelta(current_temp, target_temp):
        # need this be joules per unit time? likely
        joules = self.host.env._getHeatCapacity(current_temp, target_temp)
        pulse_width_in_seconds = joules/self._heatInJoules()
        return pulse_width_in_seconds

    def _compose(self):
        initemp = self._readThermoCouple()
        for stage in self.sequence:
            seg = rampHoldStage(stage.ramp_rate,
                                self.temp_unit,
                                initemp,
                                stage.stop_at,
                                stage.hold_time,
                                self)
            initemp = seg.stop_at
            self.plan.append(seg)

    def _hold(self, at, duration):
    	hold_start = time.time()
    	time_since = hold_start
    	while time_since < duration:
    		# wait to cool below target
    		# to re-initialize pulse sequence
    		while cur_temp >= at:
            	time.sleep(1)
            	cur_temp = self._readThermoCouple()
        	pulse_width = self._getRequiredPulseWidthForTempDelta(cur_temp, at)
        	self.pwm.set_active_time(pulse_width)
            self.pwm.pulse()
        	time_since = time.time()

    def notifyHost(msg):
    	self.host.receiveMessage(msg)

    def run(self):
        lock_status_or_error = self.host._requestLock()
        # begin executing from plan
        for seg in self.plan:
            for i in range(seg._pulses_in_stage):
                cur_temp = self._readThermoCouple()
                pulse_end_target = seg.pulse_plan[i][1]
                while cur_temp >= pulse_end_target:
                    time.sleep(1)
                    cur_temp = self._readThermoCouple()
                pulse_width = self._getRequiredPulseWidthForTempDelta(cur_temp,
                                                                      pulse_end_target)
                self.pwm.set_active_time(pulse_width)
            	self.pwm.pulse()
            if seg.hold_time > 0:
            	self._hold(seg._pulse_plan[i][1], seg.hold_time)
        # conclude FiringPlan



                


    def getRampHeatEnergy():
        raise NotImplemented

    def _readThermoCouple(self):
        '''wraps max31855 read method, means
        self.tcdriver.data will retarin
        valud from last method call'''
        return self.tcdriver.get()

    def _calculateEstimatedFiringTime(self):
        total_time_in_seconds = 0
        for stage in self.sequence:
            total_time_in_seconds += est_time
        return total_time_in_seconds

    def _getPulseSchema(self):
        pulse_count = math.ceil(
            self._calculateEstimatedFiringTime / self.pwm._full_pulse)
