import time
import os
from random import randint
import RPi.GPIO as GPIO 
""" 
This is an example for four lanes at a single junction
in which the traffic density is calculated using the 
ITLC algorithm and gives the number of vehicles passed over time.
The variables in calculating time in the algorithm have taken to be approximately
equal for all four lanes except the farthest distance which depends on the density
density is given by number of vehicles
time is calculated by dividing the density with
number of vehicles passing in one sec
"""
GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
GND = [6,9,14,20,25]
IO = [3,5,7,8,10,12,11,13,15,16,18,19,21,23,22,24,26]
lowv = [1,17]
highv = [2,4]
#o12 = IO[:12]
o12 = [15,16,22,36,11,18,37,7,12,33,29,40]


for i in range(12):

    if i in [2,3,6,9]:
        GPIO.setup(o12[i], GPIO.OUT, initial=GPIO.HIGH) # lane 1 gets the default green signal
    #elif :
        #GPIO.setup(o12[i], GPIO.OUT, initial=GPIO.HIGH)
    else:
        GPIO.setup(o12[i], GPIO.OUT, initial=GPIO.LOW)
#no of vehicles passing in one sec is denoted by n
n = 2
#considering that vehicle counting process takes a time of 'yolo' sec
yolo = 5
current_signal = 30
previous_signal = 30
total_passed_ITLC = 0
total_passed_FCTL = 0
index = 0
time_array = [0,0,0,0]
residue = 0

def random_yolo():
    i = 0
    for j in range(yolo):
        i = i + randint(0,2)
    return i 
def counter(lanes):
    for l in lanes:
        if l!=current_lane:
            l.get_count()
            l.set_count()
        else:
            l.set_zero()
def max_density(lanes,lanes_cars):
    total_passed_ITLC = total_passed_ITLC + max(lanes_cars) 
    return lanes[lanes_cars.index(max(lanes_cars))]
def time_set(lanes):
    for l in lanes:
        if l!=current_lane:
            l.time=current_signal
def current():
    if time_array[i] + residue < current_signal :
        total_passed_FCTL = total_passed_FCTL + residue*n + (time_array[i]) * n
        residue =0
    else :
        total_passed_FCTL = total_passed_FCTL + current_signal*n 
        residue = (time_array[i] + residue - current_signal)
    

class mylanes(object):
    def __init__(self,color,number_of_cars,time):
        self.color=color
        self.number_of_cars=number_of_cars
        self.time=time
        self.pins = []
    def get_count(self):
        os.chdir(r"/home/pi/Desktop")
        os.system("python command.py")
    def set_zero(self):
        self.color="red"
        self.number_of_cars = 0
    def red_amber(self):
        self.color="green"
    def g2y(self):
        GPIO.output(self.pins[2],GPIO.LOW)
        GPIO.output(self.pins[1],GPIO.HIGH)
    def ry(self):
        GPIO.output(self.pins[1],GPIO.HIGH)
    def y2r(self):
        GPIO.output(self.pins[1],GPIO.LOW)
        GPIO.output(self.pins[0],GPIO.HIGH)
    def ry2g(self):
        GPIO.output(self.pins[1],GPIO.LOW)
        GPIO.output(self.pins[0],GPIO.LOW)
        GPIO.output(self.pins[2],GPIO.HIGH)
   

class Lane1(mylanes):
    def __init__(self,color,number_of_cars,time):
        mylanes.__init__(self,color,number_of_cars,time)
        self.pins = o12[:3]   
    def set_count(self):
        f = open("/home/pi/Desktop/lane1.txt","r")        
        self.number_of_cars = int(f.read()) + random_yolo()        
        self.time = int(self.number_of_cars/n)
        time_array[0] = self.time
        if self.time > 60:
            self.time = 60
        elif self.time < 10:
            self.time = 10
        f.close()


class Lane2(mylanes):
    def __init__(self,color,number_of_cars,time):
        mylanes.__init__(self,color,number_of_cars,time)
        self.pins=o12[3:6]    
    def set_count(self):
        f = open("/home/pi/Desktop/lane2.txt","r")        
        self.number_of_cars = int(f.read()) + random_yolo()        
        self.time = int(self.number_of_cars/n)
        time_array[1] = self.time
        if self.time > 60:
            self.time = 60
        elif self.time < 10:
            self.time = 10
        f.close()
    

class Lane3(mylanes):
    def __init__(self,color,number_of_cars,time):
        mylanes.__init__(self,color,number_of_cars,time)
        self.pins=o12[6:9]    
    def set_count(self):
        f = open("/home/pi/Desktop/lane3.txt","r")        
        self.number_of_cars = int(f.read()) + random_yolo()
        self.time = int(self.number_of_cars/n)
        time_array[2] = self.time
        if self.time > 60:
            self.time = 60
        elif self.time < 10:
            self.time = 10
        f.close()
    

class Lane4(mylanes):
    def __init__(self,color,number_of_cars,time):
        mylanes.__init__(self,color,number_of_cars,time)
        self.pins=o12[9:]
    def set_count(self):
        f = open("/home/pi/Desktop/lane4.txt","r")    
        self.number_of_cars = int(f.read()) + random_yolo()        
        self.time = int(self.number_of_cars/n)
        time_array[3] = self.time
        if self.time > 60:
            self.time = 60
        elif self.time < 10:
            self.time = 10
        f.close()
    
lane1 = Lane1("green",0,60)
lane2 = Lane2("red",0,60)
lane3 = Lane3("red",0,60)
lane4 = Lane4("red",0,60)
alllanes = [lane1,lane2,lane3,lane4]
def cars():
    return [lane1.number_of_cars,lane2.number_of_cars,lane3.number_of_cars,lane4.number_of_cars]
current_lane = lane1
previous_lane = lane1

while True:
    index = index + 1
    seconds = time.time()
    time.sleep(current_signal-yolo)
    counter(alllanes)
    previous_lane=current_lane
    current_lane=max_density(alllanes,cars())    
    previous_signal=current_signal
    current_signal=current_lane.time
    current_lane.red_amber()
    time_set(alllanes)
    time.sleep(seconds + previous_signal - time.time())
    #yellow on for 3 sec
    previous_lane.g2y()
    current_lane.ry()
    time.sleep(3)
    #change lights for current and previous lane
    previous_lane.y2r()
    current_lane.ry2g()
    current()
    print("Number of cars passed by ITLC " + total_passed_ITLC)
    print("Number of cars passed by FCTL " + total_passed_FCTL)
    print("Percentage of improvement " + (((total_passed_ITLC - total_passed_FCTL)/total_passed_FCTL) * 100))

   









