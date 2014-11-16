#!/usr/bin/python

import smbus
import math
import time
import numpy as np
# Power management registers
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a,b):
    return math.sqrt((a*a)+(b*b))

def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)

bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68       # This is the address value read via the i2cdetect command
def getInfo():

    # Now wake the 6050 up as it starts in sleep mode
    bus.write_byte_data(address, power_mgmt_1, 0)

    gyro_xout = read_word_2c(0x43)
    gyro_yout = read_word_2c(0x45)
    gyro_zout = read_word_2c(0x47)

    accel_xout = read_word_2c(0x3b)
    accel_yout = read_word_2c(0x3d)
    accel_zout = read_word_2c(0x3f)

    accel_xout_scaled = accel_xout / 16384.0
    accel_yout_scaled = accel_yout / 16384.0
    accel_zout_scaled = accel_zout / 16384.0
    return [accel_xout,accel_yout,accel_zout,accel_xout_scaled,accel_yout_scaled,accel_zout_scaled,get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled),get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)]

filterData={"samples":[],"aveSamples":[0.0,0.0,0.0]}
filterSize=10
def updateFilter(samples):
	filterData["samples"].append(samples[0:3])
	filterData["aveSamples"][0]+=samples[0]
	filterData["aveSamples"][1]+=samples[1]
	filterData["aveSamples"][2]+=samples[2]
	
	if len(filterData["samples"])>=filterSize:
		last=filterData["samples"].pop(0)
		filterData["aveSamples"][0]-=last[0]
		filterData["aveSamples"][1]-=last[1]
		filterData["aveSamples"][2]-=last[2]

zeroing=[332.78, 451.44, 17340.36]
speed_mapped={"low":2,"medium":5,"high":9}
def speedMap(val):
	if val > speed_mapped["high"]:
		return 3
	elif val > speed_mapped["medium"]:
		return 2
	elif val > speed_mapped["low"]:
		return 1
	else:
		return 0
	
def calcState(state):
	heading={"speed":0,"turn":0}
	# x negative = turn right
	# x positive = turn left
	# y negative = forward
	# y positive = reverse
	factor=1600 # this should bring everything close to a range of -10 to 10
	zeed = (np.array(state)-np.array(zeroing))/factor # zeroed state
	if zeed[0] > 0:
		heading["turn"] = speedMap(abs(zeed[0]))
	elif zeed[0] < 0:
		heading["turn"] = -1*speedMap(abs(zeed[0]))
	if zeed[1] > 0:
		heading["speed"] = speedMap(abs(zeed[1]))
	elif zeed[1] < 0:
		heading["speed"] = -1*speedMap(abs(zeed[1]))
	return heading
	
while True:
    res = getInfo()
    updateFilter(res)
    state=[filterData["aveSamples"][0]/len(filterData["samples"]), filterData["aveSamples"][1]/len(filterData["samples"]), filterData["aveSamples"][2]/len(filterData["samples"])]
    print calcState(state)
    #if len(filterData["samples"]) > 5:
	#	print "%.2f %.2f %.2f -- %.2f %.2f %.2f" % (res[0],res[1],res[2],filterData["aveSamples"][0]/len(filterData["samples"]), filterData["aveSamples"][1]/len(filterData["samples"]), filterData["aveSamples"][2]/len(filterData["samples"]))
    time.sleep(0.1)
