#!/usr/bin/env python3
import gpiozero  
import PCF8591 as ADC
import time
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
import busio
from board import SCL, SDA

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x40)  # default 0x40
pca.frequency = 50

L_BTN_BCM = 17   
R_BTN_BCM = 18   
btn_L = gpiozero.Button(L_BTN_BCM, pull_up=True)
btn_R = gpiozero.Button(R_BTN_BCM, pull_up=True)

def set_angle(ID, angle):
    servo_angle = servo.Servo(pca.channels[ID], min_pulse=500, max_pulse=2400, actuation_range=180)
    servo_angle.angle = angle

angle = [90, 90, 90, 90, 90]  
speed = 1                    
forward = 1
reverse = -1

mark = None
state_num = None
state_mark = None
servoD_mark = 0

def setup():
    ADC.setup(0X48)
    
    set_angle(0, 90)
    set_angle(1, 90)
    set_angle(2, 90)
    set_angle(3, 90)
    set_angle(4, 90)

def ctrl_range(raw, max_genout, min_genout):
    if raw > max_genout:
        raw_output = max_genout
    elif raw < min_genout:
        raw_output = min_genout
    else:
        raw_output = raw
    return int(raw_output)

def rotation(ID, direction, speed):
    global angle
    if ID is None:
        pass
    else:
        if direction == 1:
            angle[ID] += speed
        else:
            angle[ID] -= speed
        angle[ID] = ctrl_range(angle[ID], 180, 0)  
        set_angle(ID, angle[ID])

def move_servo(value):
    if value == 1:          
        rotation(0, forward, speed)
    elif value == -1:
        rotation(0, reverse, speed)
    elif value == 2:        
        rotation(1, forward, speed)
    elif value == -2:
        rotation(1, reverse, speed)
    elif value == 3:        
        rotation(2, forward, speed)
    elif value == -3:
        rotation(2, reverse, speed)
    elif value == 4:        
        rotation(4, forward, speed)
    elif value == -4:
        rotation(4, reverse, speed)
    elif value == 5:     
        rotation(3, forward, speed)
    elif value == -5:
        rotation(3, reverse, speed)
    else:
        rotation(None, reverse, speed)

def joystick():
    global state_num, state_mark, servoD_mark
    state = ['home','L-pressed',  'L-down', 'L-up',  'L-right', 'L-left',
             'R-home','R-pressed', 'R-down', 'R-up',  'R-left', 'R-right']
    value = None
    
    if btn_L.is_pressed:  
        value = -6
        state_num = 1
        servoD_mark = 1
    elif btn_R.is_pressed: 
        value = 6
        state_num = 7
        servoD_mark = 0
    else:
        value = 0
        state_num = 0

    if ADC.read(0) <= 30:  # servo A
        value = 1 
        state_num = 2
    elif ADC.read(0)>= 210 :   # servo A
        value = -1
        state_num = 3

    if ADC.read(1) >= 210:   # servo B
        value = 2
        state_num = 4
    elif ADC.read(1) <= 30: 
        value = -2
        state_num = 5

    if ADC.read(2) <= 30: # servo C
        value = 3
        state_num = 8
    elif ADC.read(2)>= 210 :   # servo C
        value = -3 
        state_num = 9
    
    if servoD_mark == 1:
        if ADC.read(3) <= 30:   # servo D
            value = 5
            state_num = 10
        elif ADC.read(3) >= 210: 
            value = -5
            state_num = 11
    else:
        if ADC.read(3) <= 30:   # servo E
            value = 4
            state_num = 10
        elif ADC.read(3) >= 210: 
            value = -4
            state_num = 11
    if state_mark != state_num: # print state.
        print(state[state_num])
        state_mark = state_num
    return value

def loop():
    global mark
    value = joystick()
    move_servo(value)
    if mark != value:
        mark = value
    time.sleep(0.01)

def destroy():
    btn_L.close()
    btn_R.close()
    pca.deinit() 

if __name__ == '__main__':
    setup()
    try:
        while True:
            loop()
    except KeyboardInterrupt: 
        destroy()
        print("\nProgram exited, resources cleaned up")