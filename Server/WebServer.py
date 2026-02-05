#!/usr/bin/python3
# File name   : setup.py
# Author      : Adeept Devin
# Date        : 2022/7/12
import time
import threading
import RPIservo
import os
import socket
import info
import gpiozero
import PCF8591 as ADC
import asyncio
import websockets
import json
import app


state_num = None
state_mark = None
servoD_mark = None
joystick_mark = 1
joystick_button_mark = 0

# The servo turns to the initial position.
scGear = RPIservo.ServoCtrl()
scGear.moveInit()
scGear.start()

# Get the initial angle of the servo.
init_servo0 = scGear.initAngle[0]
init_servo1 = scGear.initAngle[1]
init_servo2 = scGear.initAngle[2]
init_servo3 = scGear.initAngle[3]
init_servo4 = scGear.initAngle[4]

curpath = os.path.realpath(__file__)
thisPath = "/" + os.path.dirname(curpath)

direction_command = 'no'
turn_command = 'no'

# WEB interface to control the servo.
def robotCtrl(command_input, response):
    global direction_command, turn_command
    #print(command_input)
    if command_input == "A_add":
        scGear.singleServo(0, 1, 1) # (servoPort, direction, speed)

    elif command_input == "A_minus":
        scGear.singleServo(0, -1, 1)

    elif command_input == "AS":
        scGear.stopWiggle()

    elif command_input == "B_add":
        scGear.singleServo(1, -1, 1) # (servoPort, direction, speed)

    elif command_input == "B_minus":
        scGear.singleServo(1, 1, 1)

    elif command_input == "BS":
        scGear.stopWiggle()
        
    elif command_input == "C_add":
        scGear.singleServo(2, 1, 1) # (servoPort, direction, speed)
    elif command_input == "C_minus":
        scGear.singleServo(2, -1, 1)
    elif command_input == "CS":
        scGear.stopWiggle()
        
    elif command_input == "D_add":
        scGear.singleServo(3, 1, 1) # (servoPort, direction, speed)
    elif command_input == "D_minus":
        scGear.singleServo(3, -1, 1)
    elif command_input == "DS":
        scGear.stopWiggle()
        
    elif command_input == "E_add":
        scGear.singleServo(4, 1, 1) # (servoPort, direction, speed)
    elif command_input == "E_minus":
        scGear.singleServo(4, -1, 1)
    elif command_input == "ES":
        scGear.stopWiggle()

    elif command_input == 'save_pos':
        Pos = scGear.servoAngle()
        newPos = []
        for i in range(0, 5):
            newPos.append(Pos[i])
        print("save_pos:",newPos)
        scGear.newPlanAppend(newPos)
    
    elif command_input == 'stop':
        scGear.moveThreadingStop()

    elif command_input == 'cerate_Plan':
        scGear.createNewPlan()

    elif command_input == 'plan':
        scGear.planThreadingStart()
        scGear.angleUpdate()

    elif command_input == 'save_Plan':
        scGear.savePlanJson()
        pass

def configInitAngle(command_input, response):
    pass

# Joystick initialization.
def joystickSetup():
    ADC.setup(0X48)
    global btn_L, btn_R
    btn_L = gpiozero.Button(17, pull_up=True)  # Left button - BCM 17
    btn_R = gpiozero.Button(18, pull_up=True)  # Right button - BCM 18

# read joystick value.
def joystick():
    global state_num, state_mark, servoD_mark
    state = ['home','L-pressed', 'L-up', 'L-down', 'L-left', 'L-right',
             'R-home','R-pressed', 'R-up', 'R-down', 'R-left', 'R-right']
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

# Control the servo through the joystick.
def joystick_move_servo(value):
    global joystick_mark, joystick_button_mark
    if value != 0:
        joystick_mark = 1
    if value == 1:          # servo A
        scGear.singleServo(0, 1, 1) # (servo_ID, direction, speed)
        print(scGear.servoAngle())
    elif value == -1:
        scGear.singleServo(0, -1, 1)
        print(scGear.servoAngle())
    elif value == 2:        # servo B
        scGear.singleServo(1, 1, 1)
    elif value == -2:
        scGear.singleServo(1, -1, 1)
    elif value == 3:        # servo C
        scGear.singleServo(2, 1, 1)
    elif value == -3:
        scGear.singleServo(2, -1, 1)
    elif value == 4:        # servo D
        scGear.singleServo(3, 1, 1)
    elif value == -4:
        scGear.singleServo(3, -1, 1)
    elif value == 5:        # servo E
        scGear.singleServo(4, 1, 1)
    elif value == -5:
        scGear.singleServo(4, -1, 1)
    elif value == 6:
        scGear.planThreadingStart()
        scGear.angleUpdate()
        joystick_button_mark = 1
    elif value ==  -6:
        scGear.moveThreadingStop()
        joystick_button_mark = 0
    else:   # servo stop
        if joystick_mark == 1 and joystick_button_mark == 0:
            scGear.stopWiggle()
            joystick_mark = 0
    
def joystickControl():
    joystickSetup()
    while True:
        value = joystick()
        joystick_move_servo(value)
        time.sleep(0.05)

async def check_permit(websocket):
    print("check_permit")
    while True:
        recv_str = await websocket.recv()
        cred_dict = recv_str.split(":")
        if cred_dict[0] == "admin" and cred_dict[1] == "123456":
            response_str = "congratulation, you have connect with server\r\nnow, you can do something else"
            await websocket.send(response_str)
            return True

async def recv_msg(websocket):
    print("recv_msg")
    while True:
        response = {
            'status': 'ok',
            'title': '',
            'data': None
        }
        data = ''
        data = await websocket.recv()
        try:
            data = json.loads(data)
        except Exception as e:
            print("Not A JSON")
        
        if not data:
            continue
        #print("data:", data)
        if data != 'get_info':
            print(data)
        if isinstance(data, str):
            robotCtrl(data, response)
            configInitAngle(data, response)
        
        if data == "get_info":
            response['title'] = 'get_info'
            response['data'] = [info.get_cpu_tempfunc(), info.get_cpu_use(), info.get_ram_info()]

        response = json.dumps(response)
        await websocket.send(response)

async def main_logic(websocket, path):
    await check_permit(websocket)
    await recv_msg(websocket)

if __name__ == "__main__":
    global flask_app
    flask_app = app.webapp()
    flask_app.startThread()

    joystickControlThreading=threading.Thread(target=joystickControl)
    joystickControlThreading.setDaemon(True)
    joystickControlThreading.start()

    while True:
        try:
            start_server = websockets.serve(main_logic, '0.0.0.0', 8888)
            asyncio.get_event_loop().run_until_complete(start_server)
            print('waiting for connection...')
            break
        except Exception as e:
            print(e)
    try:
        asyncio.get_event_loop().run_forever()
    except Exception as e:
        print(e)