#!/usr/bin/env python
import threading, time, spidev, math
import RPi.GPIO as GPIO
import Functions2 as Functions
import VL53L0X

print("\n ~~~  Welcome to the Pumpkin Pals' Birdemic Centripetal Force Sensor  ~~~\n\n")

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

dummy = input("The arm will rotate automatically to the correct position for radial measurement.  Make sure the two rod ends are approximately balanced, though exact counterweights will be calculated later.  Press ENTER to continue.")  
try:
    Functions.homing()
    print("\nCarriage lined up with distance sensor!  Disregard the device info directly below.")

    tof = VL53L0X.VL53L0X()
    tof.start_ranging(VL53L0X.VL53L0X_GOOD_ACCURACY_MODE)
    distance = tof.get_distance()
    print("\nRadius of Center of Mass from Center Rod measured to be ", distance, " mm.")

    print("\nNow measure your desired mass, and after entering it the approximate counterweight mass will be given.  Make sure the counterweight is close to the value given, though perfect accuracy isn't necessary.")
    mass = float(input("\nEnter your Mass in Grams: "))
    counterweight = ((mass+57)*distance)/120 - 57
    print("\nThe recommended counterweight is ", round(counterweight, 0), " grams.  Add the counterweight now, rounding up to the nearest 50g.")

    print("Then, decide how many rotations per second to specify.  The actual speed will be slower, so the device will measure it for you.")
    reps = 20
    speed = float(input("\nEnter Rotations per Second: "))
    timestep = 1/(speed*205)

    stepperthread = threading.Thread(target=Functions.stepper, args=(reps, timestep))
    photothread = threading.Thread(target=Functions.photodiode, args=(speed,mass,distance))

    stepperthread.start()
    photothread.start()

    stepperthread.join()
    photothread.join()

except KeyboardInterrupt:
    GPIO.cleanup()
except Exception as e:
    print('Unexpected Error: ', e)
    GPIO.cleanup()


