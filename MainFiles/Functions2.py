#!/usr/bin/env python3
"""
ADC MCP3008 python 3.7.3 tested
Ran Yang 9/27/2020
Connection:
VDD -> 3.3V
VREF -> 3.3V
AGND -> GND
CLK -> GPIO11
Dout -> GPIO09
Din -> GPIO10
CS -> GPIO8
DGND -> GND

Analog input -> CH0 ~ CH7
"""

import RPi.GPIO as GPIO
import time, spidev, math

out1 = 13
out2 = 11
out3 = 15
out4 = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setup(out1,GPIO.OUT)
GPIO.setup(out2,GPIO.OUT)
GPIO.setup(out3,GPIO.OUT)
GPIO.setup(out4,GPIO.OUT)

spi = spidev.SpiDev() #open spi bus
spi.open(0,0) #open(bus, device)
spi.max_speed_hz=1000000
spi.mode = 0b00 #spi modes; 00,01,10,11

def read_adc(channel):
    if not 0 <= channel <= 7:
        raise IndexError('Invalid. enter 0, 1, ..., 7' )
    """datasheet page 19 about setting sgl/diff bit to high, hence we add 8 = 0b1000
    left shift 4 bits to make space for the second byte of data[1]"""
    request = [0x1, (8+channel) << 4, 0x0] # [start bit, configuration, listen space]
    data = spi.xfer2(request) #data is recorded 3 bytes: data[0] - throw away, data[1] - keep last 2 bits, data[2] - keep all
    data10bit = ((data[1] & 3) << 8) + data[2] #shfit bits to get the 10 bit data
    return data10bit

def photodiode(speed, mass, distance):
    # Setup.  time_step is time between measurements, dark_volt is the fraction
    # of ambient light reached for the program to recognize the carriage has
    # passed over it, usually not much smaller than ambient voltage with our setup.
    time_step = 0.001
    volts = []
    times = []
    rotations = []
    print("\nReading AMBIENT LIGHT in 0.5 seconds")
    time.sleep(0.5)
    ambient = read_adc(0) * (3.3/1024)
    dark_volt = 0.93 * ambient
    nummeasure = int(round((20/speed)*1000*0.75, 0))
    
    # The main loop that runs while taking data on timestamps and voltage put out
    # by the photodiode.  Un-comment the print line below if a stream of real-time
    # measurements is desired.
    darkflag = False
    t = -time_step
    counts = 0
    print("\nTaking measurements!  For accurate measurements, do not hinder the device!")
    for i in range(nummeasure):
        t = t + time_step
        v_volt = read_adc(0) * (3.3/1024)
        #print("The input voltage is ", v_volt)
        if darkflag == False and v_volt < dark_volt:
            darkflag = True
            counts += 1
            print("Count: ", counts)
            rotations.append(time.time())
        if darkflag == True and v_volt > dark_volt:
            darkflag = False
        volts.append(v_volt)
        times.append(t)
        time.sleep(time_step)

    # The loop which creates a list of periods calculated with timestamps.  Before
    # appending to the periods list, it removes timestamps unrealistically close to
    # the previous due to any error or "noise" in the signal.
    periods = []
    try:
        for i in range(0, len(rotations)-1):
            while rotations[i+1] - rotations[i] < 0.1:
                rotations.pop(i+1)
            periods.append(rotations[i+1] - rotations[i])
    except IndexError:
        pass
    try:
        finalperiod = sum(periods) / len(periods)
        centripetal = (4*(math.pi)**2 * (mass/1000) * (distance/1000)) / ((finalperiod)**2)
        print("\nUsing the formula Fc = (4pi^2 mr) / T^2, the centripetal force can be calculated:\n ")
        print("Centripetal Force: ", centripetal, " N")
        print("Mass: ", mass, " g")
        print("Radius: ", distance, " mm")
        print("Acceleration: ", centripetal/mass, " ms^-2")
        print("Period: ", finalperiod, " s")
        print("Frequency: ", 1/finalperiod, " Hz")
        print("Angular Frequency: ", 2*math.pi*(1/finalperiod), " rad/s") 
        print("Counts while Measuring: ", counts)
        
        print("\n\nPowering Down in a few seconds... \nThank you for using the Birdemic Centripetal Force Sensor!\n")
    except:
        print("\nNo rotations were sensed!  Run the program again.\n")
    
    
def stepper(reps, timestep):
    out1 = 13
    out2 = 11
    out3 = 15
    out4 = 12

    GPIO.setmode(GPIO.BOARD)
    outs = [out1, out2, out3, out4]
    for out in outs:
        GPIO.setup(out, GPIO.OUT)

    #pattern = [[1,0,0,0], [1,0,1,0], [0,0,1,0], [0,1,1,0],
    #           [0,1,0,0], [0,1,0,1], [0,0,0,1], [1,0,0,1]]
    pattern = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]]

    x = int(reps*200)
    if x>0 and x<=100000:
        for i in range(x):
            throws = pattern[i%len(pattern)]
            for j in range(len(outs)):
                GPIO.output(outs[j], throws[j])
            time.sleep(timestep)
            #print(i)

    GPIO.cleanup()
    

def homing():
    i = 0
    print("Reading ambient light and homing in 3 seconds...")
    time.sleep(3)
    ambient = read_adc(0) * (3.3/1024)
    dark_volt = 0.94 * ambient
    v_volt = ambient
    timestep = 0.03 #Change this for speed!!! 0.003 is fast, 0.01 is slow
    out1 = 13
    out2 = 11
    out3 = 15
    out4 = 12

    GPIO.setmode(GPIO.BOARD)
    outs = [out1, out2, out3, out4]
    for out in outs:
        GPIO.setup(out, GPIO.OUT)

    #pattern = [[1,0,0,0], [1,0,1,0], [0,0,1,0], [0,1,1,0],
    #           [0,1,0,0], [0,1,0,1], [0,0,0,1], [1,0,0,1]]
    pattern = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]]

    i=0
    while v_volt > dark_volt:
        #print(v_volt)
        throws = pattern[i%len(pattern)]
        for j in range(len(outs)):
            GPIO.output(outs[j], throws[j])
        time.sleep(timestep)
        #print(i)
        i+=1
        v_volt = read_adc(0) * (3.3/1024)
    print("\nWaiting for vibrations to cease...")
    time.sleep(3) #freeze the stepper in place for 1s
    GPIO.cleanup()

