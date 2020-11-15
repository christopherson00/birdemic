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
    time_step = 0.005
    volts = []
    times = []
    rotations = []
    print("\nReading AMBIENT LIGHT in 0.5 seconds")
    time.sleep(0.5)
    ambient = read_adc(0) * (3.3/1024)
    dark_volt = 0.95 * ambient
    nummeasure = int(round((20/speed)*160*0.8, 0))
    
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
        print("\n\nThe average period is ", finalperiod)

        centripetal = (4*(math.pi)**2 * (mass/1000) * (distance/1000)) / ((finalperiod)**2)
        print("\nUsing the formula Fc = (4pi^2 mr) / T^2, the centripetal force can be calculated:\n ", centripetal, " N.")
        print("Centripetal Force: ", centripetal, " N")
        print("Mass: ", mass, " g")
        print("Radius: ", distance, " mm")
        print("Acceleration: ", centripetal/mass, " ms^-2")
        print("Period: ", finalperiod, " s")
        print("Frequency: ", 1/finalperiod, " Hz")
        print("Angular Frequency: ", 2*math.pi*(1/finalperiod), " rad/s") 
        print("Counts while Measuring: ", counts)
        
        print("\n\nPowering Down... \nThank you for using the Birdemic Centripetal Force Sensor!\n")
    except:
        print("\nNo rotations were sensed!  Run the program again.\n")
    
    
def stepper(reps, timestep):
    i = 0
    y = 0
    out1 = 13
    out2 = 11
    out3 = 15
    out4 = 12
    GPIO.output(out1,GPIO.LOW)
    GPIO.output(out2,GPIO.LOW)
    GPIO.output(out3,GPIO.LOW)
    GPIO.output(out4,GPIO.LOW)
    x = int(reps*400)
    if x>0 and x<=100000:
        for y in range(x,0,-1):
            if i==0:
                GPIO.output(out1,GPIO.HIGH)
                GPIO.output(out2,GPIO.LOW)
                GPIO.output(out3,GPIO.LOW)
                GPIO.output(out4,GPIO.LOW)
                time.sleep(timestep)
            elif i==1:
                GPIO.output(out1,GPIO.HIGH)
                GPIO.output(out2,GPIO.HIGH)
                GPIO.output(out3,GPIO.LOW)
                GPIO.output(out4,GPIO.LOW)
                time.sleep(timestep)
            elif i==2:
                GPIO.output(out1,GPIO.LOW)
                GPIO.output(out2,GPIO.HIGH)
                GPIO.output(out3,GPIO.LOW)
                GPIO.output(out4,GPIO.LOW)
                time.sleep(timestep)
            elif i==3:
                GPIO.output(out1,GPIO.LOW)
                GPIO.output(out2,GPIO.HIGH)
                GPIO.output(out3,GPIO.HIGH)
                GPIO.output(out4,GPIO.LOW)
                time.sleep(timestep)
            elif i==4:
                GPIO.output(out1,GPIO.LOW)
                GPIO.output(out2,GPIO.LOW)
                GPIO.output(out3,GPIO.HIGH)
                GPIO.output(out4,GPIO.LOW)
                time.sleep(timestep)
            elif i==5:
                GPIO.output(out1,GPIO.LOW)
                GPIO.output(out2,GPIO.LOW)
                GPIO.output(out3,GPIO.HIGH)
                GPIO.output(out4,GPIO.HIGH)
                time.sleep(timestep)
            elif i==6:
                GPIO.output(out1,GPIO.LOW)
                GPIO.output(out2,GPIO.LOW)
                GPIO.output(out3,GPIO.LOW)
                GPIO.output(out4,GPIO.HIGH)
                time.sleep(timestep)
            elif i==7:
                GPIO.output(out1,GPIO.HIGH)
                GPIO.output(out2,GPIO.LOW)
                GPIO.output(out3,GPIO.LOW)
                GPIO.output(out4,GPIO.HIGH)
                time.sleep(timestep)
            if i==7:
                i=0
                continue
            i=i+1

    GPIO.cleanup()

def homing():
    i = 0
    print("Reading ambient light and homing in 3 seconds...")
    time.sleep(3)
    ambient = read_adc(0) * (3.3/1024)
    dark_volt = 0.9 * ambient
    v_volt = ambient
    timestep = 0.01
    out1 = 13
    out2 = 11
    out3 = 15
    out4 = 12
    GPIO.output(out1,GPIO.LOW)
    GPIO.output(out2,GPIO.LOW)
    GPIO.output(out3,GPIO.LOW)
    GPIO.output(out4,GPIO.LOW)
    while v_volt > dark_volt:
        v_volt = read_adc(0) * (3.3/1024)
        if i==0:
            GPIO.output(out1,GPIO.HIGH)
            GPIO.output(out2,GPIO.LOW)
            GPIO.output(out3,GPIO.LOW)
            GPIO.output(out4,GPIO.LOW)
            time.sleep(timestep)
        elif i==1:
            GPIO.output(out1,GPIO.HIGH)
            GPIO.output(out2,GPIO.HIGH)
            GPIO.output(out3,GPIO.LOW)
            GPIO.output(out4,GPIO.LOW)
            time.sleep(timestep)
        elif i==2:
            GPIO.output(out1,GPIO.LOW)
            GPIO.output(out2,GPIO.HIGH)
            GPIO.output(out3,GPIO.LOW)
            GPIO.output(out4,GPIO.LOW)
            time.sleep(timestep)
        elif i==3:
            GPIO.output(out1,GPIO.LOW)
            GPIO.output(out2,GPIO.HIGH)
            GPIO.output(out3,GPIO.HIGH)
            GPIO.output(out4,GPIO.LOW)
            time.sleep(timestep)
        elif i==4:
            GPIO.output(out1,GPIO.LOW)
            GPIO.output(out2,GPIO.LOW)
            GPIO.output(out3,GPIO.HIGH)
            GPIO.output(out4,GPIO.LOW)
            time.sleep(timestep)
        elif i==5:
            GPIO.output(out1,GPIO.LOW)
            GPIO.output(out2,GPIO.LOW)
            GPIO.output(out3,GPIO.HIGH)
            GPIO.output(out4,GPIO.HIGH)
            time.sleep(timestep)
        elif i==6:
            GPIO.output(out1,GPIO.LOW)
            GPIO.output(out2,GPIO.LOW)
            GPIO.output(out3,GPIO.LOW)
            GPIO.output(out4,GPIO.HIGH)
            time.sleep(timestep)
        elif i==7:
            GPIO.output(out1,GPIO.HIGH)
            GPIO.output(out2,GPIO.LOW)
            GPIO.output(out3,GPIO.LOW)
            GPIO.output(out4,GPIO.HIGH)
            time.sleep(timestep)
        if i==7:
            i=0
            continue
        i=i+1
