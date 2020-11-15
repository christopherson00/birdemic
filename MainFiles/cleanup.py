import RPi.GPIO as GPIO
out1 = 13
out2 = 11
out3 = 15
out4 = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setup(out1,GPIO.OUT)
GPIO.setup(out2,GPIO.OUT)
GPIO.setup(out3,GPIO.OUT)
GPIO.setup(out4,GPIO.OUT)

GPIO.cleanup()
