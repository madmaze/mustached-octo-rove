#!/usr/bin/env python

import serial
import time
ser = serial.Serial('/dev/ttyUSB0', 9600)
c=0
neg=True
while True:
    t = -1*(c%5) if neg else c%5
    ser.write(str(t)+","+str(0)+"\n")
    print "current", t
    print ser.readline()
    time.sleep(2)
    c+=1
    if c%5==0:
    	neg=not neg
