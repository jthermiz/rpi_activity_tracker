# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 11:29:51 2017

@author: John
"""

#from scipy import signal
import numpy
import time
import math

def step_detector(D, fs):
    #D is epoch of accel data
    #fs is sample rate
    #returns time samples of when steps occur

    threshold = 0.02 #amplitude threshold ( d/dt |g| units)
    min_step_period = 0.1 #units of seconds
    n = numpy.size(D, axis=1)
    mag = numpy.zeros(n)

    #Compute Mag
    for i in range(n):
        vec = D[i,:]
        mag[i] = numpy.sqrt(numpy.dot(vec,vec))

    #Compute Diff
    dmag = numpy.diff(numpy.append(0,mag))

    #Low Pass Filter to Smooth
    #b, a = signal.butter(3, 15/(fs/2), 'low', analog=False)
    #zi = signal.lfilter_zi(b, a)
    #z, _ = signal.lfilter(b, a, dmag, zi=zi*dmag[0])

    #Threshold
    z = dmag
    tmp = z - threshold
    tmp1 = numpy.append(tmp[1:],0)

    step_times_bool = numpy.logical_and(tmp*tmp1 < 0, tmp < 0)
    step_times = numpy.squeeze(numpy.array(numpy.where(step_times_bool)))

    #Eliminate Steps That Occured Too Quickly
    good_steps = numpy.squeeze(numpy.array(numpy.where(numpy.append(0, numpy.diff(step_times)) > min_step_period*fs)))

    if numpy.size(step_times) > 0:
        step_times_clean = step_times[good_steps]
    else:
        step_times_clean = []

    return step_times_clean

def fall_detector(D, fs):
    #D is epoch of accel data
    #fs is sample rate
    #returns time samples of when falls occur
    
    #Starting processing time
    start_time = time.time()

    #finding out the length of input data
    data = D
    data_len = len(data)


    #Defining threshold values
    thres_1 = 0.1
    thres_2 = 1
    t_out = 1
    to = 0 
    counter = 0
    mag = 0
    old_mag = 0
    sample = (0,0,0)
    past_sample = (0,0,0)
    diff_ray = []
    stamp = 0    

    for i in range(1, data_len):
        sample = data[i,:]

        #Extract the x,y,z accelerometer data
        x = sample[0]
        y = sample[1]
        z = sample[2]

        #calculate the magnitude of motion 
        mag = math.sqrt(x**2 + y**2 + z**2)

        #Calculate the difference in magnitude between previous and current iteration
        mag_diff = abs(mag - old_mag)
        
	#storing the magnitude difference into an array
        diff_ray.append(mag_diff)
	
        #shift the data from mag to old_mag
        old_mag = mag

        if (mag_diff > thres_1):
            stamp = i
            counter = counter + 1

        #check to see if the threshold crossing is continuous
        check = i - stamp
        if (counter > thres_2 and check ==1):
#	    fall = 1
            print('Fall Detected')
            return 1
        elif (check > 1):
            counter = 0
            #print('Fall Not Detected')
            return []
