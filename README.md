# Inferno Digital Kiln Controller Project

## This software is intended to run on rasberry pi with MAX31855 thermocouple board and a solid state relay common in modern electric kilns.



## Major Issues and Areas of Work

### Environment model

To build a model of the environment, the device in its final stage will include an external thermometer and barometer to calculate the density of the air to in turn calculate the heat capacity of the air in the kiln's baseline environment. In this early stage, we use an estimate of STP (standard temperature and pressure). These estimates are included in envConst.json

### Current big TODOs

	- build out logging capabilities
	- Check math for gas constants, support probabilistic modeling of molar mass of air in different conditions
	- build testing environment, one that can test logic and examine logs without the necessity of running on rasberry pi with hardware set up
		-- build data / logging visualization tools for this
	- support passing degree units as parameter
	- flesh out capabilities to learn from observed changes in temperature as a function of parameters
	- support barometric pressure sensor interface


