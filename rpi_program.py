# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 00:07:53 2017

@author: John
"""

import queue
import threading
import numpy
import time
import rpi_detectors as dec
from LIS3DH import LIS3DH
import smtplib
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#global parameters
source = ''
dest = ''
user = ''

def acquire_data(q, fs, T_D_new):
    sensor = LIS3DH(debug=True)
    sensor.setRange(LIS3DH.RANGE_8G)
    data = numpy.zeros((fs*T_D_new,3))

    while True:
        # when there's no hardware
        for i in range(T_D_new*fs):         
            data[i,0] = sensor.getX()
            data[i,1] = sensor.getY()
            data[i,2] - sensor.getZ()
        
        data = numpy.random.rand(100,3)
        q.put(data)

def fall_tracker(D, fs, F_list, timestamp): #tracker class??
    #D is an epoch of length T
    #F_list is a list of the last n fall timestamps
    #timestamp is the global timestamp in seconds of the first time point in D
    #F_list_new is an updated list of fall timestemps
    n_falls = 5
    fall_time_new = dec.fall_detector(D, fs)
    
    if fall_time_new == 1:        
        F_list.append(timestamp)    #need to fix to get exact timestamp of fall
        F_list = F_list[-n_falls:]
    
    return F_list        
    
    if (dec.fall_detector(D, fs)):
        return 1
    else:
        return[]
    

def step_tracker(D, fs, S_list, timestamp):#tracker class??
    #D is an epoch of length T
    #S_list is a list of the last n steps detected
    #timestamp is the global timestamp in seconds of the first time point in D
    #S_list_new is an updated list of step timestemps
    n_steps = 50
    step_times_new = dec.step_detector(D, fs)

    for i in range(len(step_times_new)):
        tmp = timestamp + float(step_times_new)/fs
        S_list.append(tmp)

    S_list = S_list[-n_steps:]
    return S_list

def save_to_disk(D_new, filename, timestamp):
    #D_new is only the new part of the epoch
    entire_filename = filename + '_' + str(timestamp)
    numpy.save(entire_filename, D_new)

def send_alert(q):  
    #messaging overhead      
    #server=smtplib.SMTP ('smtp.gmail.com: 587')
    #server.starttls()
    #server.login(source, user)
    #server.sendmail(source, dest, 'I Have Fallen, and I can get up')
    
    #GPIO overhead for button
    button = 17
    GPIO.setup(button, GPIO.IN, GPIO.PUD_DOWN)

    #vars
    sent_flag = False
    t1 = time.time()
    t2 = time.time()

    #(not q.empty()
    while True:
        button_state = GPIO.input(button)
        t2 = time.time()
 
        if (button_state == GPIO.LOW): #if button is pressed            
            if (not sent_flag): #timeout if already sending alert is past 5 sec
                print('sent alert')
                sent_flag = True
                t1 = time.time()

        if (False): #if alert is detected
            print('sent alert')          
            q.get()        
        
        if sent_flag:
            if (t2 - t1 > 5):  #5 sec timeout
                sent_flag = False #set flag back to false
            
        
    #server.quit() #error handling to make sure this happens
    return 0

#other related functions for sms / gps


################## START MAIN ####################

# Set up some global variables
num_fetch_threads = 2
data_queue = queue.Queue()
message_queue = queue.Queue()
fs = 100 #Hz
T_D_new = 1 #second
T_D  = 4*T_D_new #seconds (multiple of T_D_new!)
timestamp = 0
filename = 'test'

# Set up some threads to acquire data
for i in range(num_fetch_threads):
    worker = threading.Thread(
        target=acquire_data,
        args=(data_queue, fs, T_D_new),
        name='worker-{}'.format(i),
    )
    worker.setDaemon(True)
    worker.start()

# Set up some threads to send alerts
sendthread = threading.Thread(target=send_alert, args= (message_queue,) ) 
sendthread.setDaemon(True)
sendthread.start()

# Set up data window D
D = data_queue.get()

for i in range(1, int(T_D/T_D_new) ):
    D_tmp = data_queue.get()
    D = numpy.concatenate((D, D_tmp))

# Save 1st D to disk
#save_to_disk(D, filename, timestamp)
timestamp = T_D

# Set up lists
F_list = []
S_list = []
Fidx = 0
t1 = -31

# Main Processing Loop
for i in range(20):
    F_list = fall_tracker(D, fs, F_list, timestamp - 4 )
    t2 = time.time()    
    if (len(F_list) > 0):        
        if (F_list[Fidx] == timestamp - 4): #if a fall occured and one didn't occur in the last 30 sec            
            if (t2 - t1 > 30): #30 second timeout
                message_queue.put(timestamp)
                t1 = time.time()            
    #S_list = step_tracker(D, fs, S_list, timestamp - 4 )
    #print(S_list)
    # Get D_new
    D_new = data_queue.get()
    D = numpy.concatenate( (D[fs:,:], D_new) )
    #save_to_disk(D_new, filename, timestamp)
    timestamp = timestamp + T_D_new
    







