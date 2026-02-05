#!/usr/bin/python3
# File name   : setup.py
# Author      : Adeept Devin
# Date        : 2022/7/12
import time
import sys
import os
import json
import threading
import random
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
import busio
from board import SCL, SDA
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x40) #default 0x40
pca.frequency = 50

curPath = os.path.realpath(__file__)
thisPath = '/' + os.path.dirname(curPath) + '/'

planJsonFileHere = open(thisPath + 'plan.json', 'r')
print(thisPath + 'plan.json')
contentPlanGose  = planJsonFileHere.read()
planGoseList = json.loads(contentPlanGose)

# Set the servo rotation angle。
def set_angle(ID, angle):
    servo_angle = servo.Servo(pca.channels[ID], min_pulse=500, max_pulse=2400,actuation_range=180)
    servo_angle.angle = angle

# Servo control.
class ServoCtrl(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.__flag = threading.Event()
        self.__flag.clear()
        self.initAngle = [90,90,90,90, 90,90,90,90, 90,90,90,90, 90,90,90,90] # 16个舵机初始角度 / 16 servo initial angle
        self.goalAngle = [90,90,90,90, 90,90,90,90, 90,90,90,90, 90,90,90,90] # 目标角度 / target angle
        self.nowAngle = [90,90,90,90, 90,90,90,90, 90,90,90,90, 90,90,90,90] # 当前角度 / current angle
        self.bufferAngle = [90.0,90.0,90.0,90.0, 90.0,90.0,90.0,90.0, 90.0,90.0,90.0,90.0, 90.0,90.0,90.0,90.0] # 缓冲角度 / buffer angle
        self.lastAngle = [90,90,90,90, 90,90,90,90, 90,90,90,90, 90,90,90,90] # 变化前的角度

        self.sc_direction = [1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1] # 舵机正常转动为1，反向转动改为-1 / The normal rotation of the servo is 1, and the reverse rotation is changed to -1
        self.scSpeed = [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0] # 舵机转动速度 / Servo rotation speed.
        self.wiggleID = 0 # 舵机号 Servo ID
        self.wiggleDirection = 1 # 自定义舵机转向,1:正转 -1:反转 / Custom servo steering, 1: Forward -1: Reverse
        self.maxAngle = 180
        self.minAngle = 0
        self.scMoveTime = 0.01
        self.goalUpdate = 0
        self.scMode = "auto"
        self.scSteps = 30
        self.scTime = 2.0
        '''
        5-DOF 机械臂 / 5-DOF Robotic Arm
        '''
        self.nowPos = [90, 90, 90, 90, 90]

        '''
        planDataSaved
        '''
        self.planJsonFile = open(thisPath + 'plan.json', 'r')
        print(thisPath + 'plan.json')
        self.contentPlan  = self.planJsonFile.read()
        self.planSave = json.loads(self.contentPlan)

    def pause(self):    # 阻塞线程 / blocking thread
        #print("......................pause......................")
        self.__flag.clear()

    def resume(self):  # 恢复线程 / resume thread
        #print("resume")
        self.__flag.set()

    # 更新舵机舵机角度值. / Update the servo angle value of the servo.
    def angleUpdate(self):
        self.goalUpdate = 1
        for i in range(0,16):
            self.lastAngle[i] = self.nowAngle[i]
        self.goalUpdate = 0
    
    # 获取舵机角度 / Get the servo angle.
    def servoAngle(self):
        #print("servoAngle():")
        return (self.nowAngle)
    # 初始化所有舵机角度/ Initialize all servo angles.
    def moveInit(self):
        for i in range(0, 16):
            set_angle(i, self.initAngle[i])
            self.lastAngle[i] = self.initAngle[i]
            self.nowAngle[i] = self.initAngle[i]
            self.bufferAngle[i] = float(self.initAngle[i])
            self.goalAngle[i] = self.initAngle[i]
        self.pause()

    def initConfig(self, ID, initInput, moveTo):
        if initInput > self.minAngle and initInput < self.maxAngle:
            self.initAngle[ID] = initInput
            if moveTo:
                set_angle(ID, self.initAngle[ID])
            else:
                print("initAngle Value Error.")
    # 舵机向某个方向转动 / The servo turns in a certain direction.
    def moveWiggle(self): 
        self.bufferAngle[self.wiggleID] += self.wiggleDirection*self.sc_direction[self.wiggleID]*self.scSpeed[self.wiggleID]
        if self.bufferAngle[self.wiggleID] > self.maxAngle: self.bufferAngle[self.wiggleID] = self.maxAngle
        elif self.bufferAngle[self.wiggleID] < self.minAngle: self.bufferAngle[self.wiggleID] = self.minAngle
        newNow = int(round(self.bufferAngle[self.wiggleID],0))
        self.nowAngle[self.wiggleID] = newNow
        self.lastAngle[self.wiggleID] = newNow
        if self.bufferAngle[self.wiggleID] < self.maxAngle and self.bufferAngle[self.wiggleID] > self.minAngle:
            set_angle(self.wiggleID, self.nowAngle[self.wiggleID])
        else:
            self.stopWiggle()
        time.sleep(self.scMoveTime)
        #print(self.servoAngle())

    # 设置某个舵机旋转到多少度. / Set the angle to which a certain servo rotates.
    def moveAngle(self,ID, angleInput):
        self.nowAngle[ID] = int(self.initAngle[ID] + angleInput)
        if self.nowAngle[self.wiggleID] > self.maxAngle: self.nowAngle[self.wiggleID] = self.maxAngle
        elif self.nowAngle[self.wiggleID] < self.minAngle: self.nowAngle[self.wiggleID]
        self.lastAngle[self.wiggleID] = self.nowAngle[self.wiggleID]
        set_angle(ID, self.nowAngle[self.wiggleID])

    # 停止转动. / Stop turning.
    def stopWiggle(self):
        self.pause()
        self.angleUpdate()
    
    # 设置某个舵机转动 / Set a single servo rotation.
    def singleServo(self, ID, directInput, speedSet): 
        self.wiggleID = ID
        self.wiggleDirection = directInput
        self.scSpeed[ID] = speedSet
        self.scMode = "wiggle"
        self.angleUpdate()
        self.resume()
    
    # 移动所有舵机到指定位置 / Move all servos to the specified position.
    def moveToPos(self, number, goalPos):
        if isinstance(goalPos, list):
            for i in range(0, len(goalPos)):
                self.goalAngle[i] = goalPos[i]
            for i in range(0, self.scSteps):
                for dc in range(0, number):
                    if not self.goalUpdate and self.goalAngle[dc] != self.nowAngle[dc]:
                        self.nowAngle[dc] = int(round((self.lastAngle[dc] + ((self.goalAngle[dc] - self.lastAngle[dc])/self.scSteps)*(i+1)), 0))
                        set_angle(dc, self.nowAngle[dc])
                        time.sleep(self.scMoveTime)
                        #print(self.nowAngle[dc])
                    #if self.goalAngle != goalPos:
                    #   self.angleUpdate()
                    #   time.sleep(self.scTime/self.scSteps)
                    #   print("???")
            self.angleUpdate()
            self.pause()
        else:
            print("goalPos not an array")

    '''
    5_DOF Robotic Arm
    '''
    # 保存角度值到本地文件
    # Save angle value to local file.
    def savePlanJson(self):
        content2write = json.dumps(planGoseList)
        file2write = open('plan.json', 'w')
        file2write.write(content2write)
        print(content2write)
        file2write.close()
        
    # 新建一个机械臂动作。
    # Create a new plan.
    def createNewPlan(self):
        global planGoseList
        planGoseList = []
        print("planGoseList:",planGoseList)
        
    # 添加一个位置到动作中
    # Add a location to the plan
    def newPlanAppend(self, nowPos):  # save Pos
        global planGoseList
        print(planGoseList)
        planGoseList.append(nowPos)
        print(planGoseList)

    # 中止动作的执行。
    # Abort the execution of the plan.
    def moveThreadingStop(self):
        self.scMode = 'stop'
        self.pause()

    # 开始执行机械臂动作。
    # Start to execute the robotic arm motion.
    def planThreadingStart(self):
        self.scMode = 'planMove'
        self.resume()

    # 执行机械臂动作。
    # execute the robotic arm motion.
    def planGoes(self):
        self.scMode = 'planMove'
        if isinstance(planGoseList, list):
            for goalPos in planGoseList:
                if self.scMode == 'stop':
                    self.pause()
                    break
                print(goalPos)
                self.moveToPos(5, goalPos) # (number, goalPos)--(5 servos, an array of angle values)
                time.sleep(1) # 
        else:
            print("planGoseList is not an array, and the content saved in the plan.json file is incorrect.")

    # 舵机控制模式
    # Servo control mode.
    def scMove(self):
        if self.scMode == "init":
            self.moveInit()
        elif self.scMode == "wiggle":
            self.moveWiggle()
        elif self.scMode == 'planMove':
            self.planGoes()
        if self.scMode == 'stop':
            self.pause()

    def run(self):
        while True:
            self.__flag.wait()
            self.scMove()

if __name__ == "__main__":
    sc = ServoCtrl()
    sc.start()
    #st.start()
    print("start!")
    goalPosList = [[90, 90], [20, 20], [160, 160]]
    
    try:
        while True:
            for goalPos in goalPosList:
                print(goalPos)
                sc.moveToPos(2, goalPos)
                time.sleep(2)
            '''
            sc.moveAngle(0, 90)
            time.sleep(1.5)
            sc.moveAngle(0, -90)
            time.sleep(1.5)
            '''
            '''
            sc.singleServo(0, -1, 1)
            time.sleep(2)
            print(sc.servoAngle())
            time.sleep(1)
            print(sc.servoAngle())
            sc.stopWiggle()
            sc.singleServo(0, 1, 1)
            time.sleep(1)
            print(sc.servoAngle())
            time.sleep(2)
            print(sc.servoAngle())
            sc.stopWiggle()
            '''
    except:
        print("stop!")
