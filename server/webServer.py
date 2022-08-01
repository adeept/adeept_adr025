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

import RPi.GPIO as GPIO
import PCF8591 as ADC

# websocket
import asyncio
import websockets

import json
import app


state_num = None
state_mark = None
servoD_mark = None
joystick_mark = 1
joystick_button_mark = 0

# 舵机转动到初始位置
# The servo turns to the initial position.
scGear = RPIservo.ServoCtrl()
scGear.moveInit()
scGear.start()

'''
joystick_sc = RPIservo.ServoCtrl()
joystick_sc.moveInit()
'''
# 获取舵机初始角度
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

def servoAngleInit():
    # A_sc.initConfig(1, init_servo0, 1)
    # B_sc.initConfig(1, init_servo1, 1)
    # C_sc.initConfig(1, init_servo2, 1)
    # D_sc.initConfig(1, init_servo3, 1)
    # E_sc.initConfig(1, init_servo4, 1)
    pass

# 修改舵机中位
# Modify the initial position of the servo.
def replace_num(initial,new_num):   #Call this function to replace data in '.txt' file
    global r
    newline=""
    str_num=str(new_num)
    with open(thisPath+"/RPIservo.py","r") as f:
        for line in f.readlines():
            if(line.find(initial) == 0):
                line = initial+"%s" %(str_num+"\n")
            newline += line
    with open(thisPath+"/RPIservo.py","w") as f:
        f.writelines(newline)

# 树莓派开启WiFi热点。
# Raspberry Pi turns on WiFi hotspot.
def ap_thread():
    os.system("sudo create_ap wlan0 eth0 Adeept_Robot 12345678")

# WEB界面控制舵机
# WEB interface to control the servo.
def robotCtrl(command_input, response):
    global direction_command, turn_command
    #print(command_input)
    if command_input == "A_add":
        scGear.singleServo(12, 1, 1) # (servoPort, direction, speed)

    elif command_input == "A_minus":
        scGear.singleServo(12, -1, 1)

    elif command_input == "AS":
        scGear.stopWiggle()

    elif command_input == "B_add":
        scGear.singleServo(13, 1, 1) # (servoPort, direction, speed)

    elif command_input == "B_minus":
        scGear.singleServo(13, -1, 1)

    elif command_input == "BS":
        scGear.stopWiggle()
        
    elif command_input == "C_add":
        scGear.singleServo(14, 1, 1) # (servoPort, direction, speed)
    elif command_input == "C_minus":
        scGear.singleServo(14, -1, 1)
    elif command_input == "CS":
        scGear.stopWiggle()
        
    elif command_input == "D_add":
        scGear.singleServo(15, 1, 1) # (servoPort, direction, speed)
    elif command_input == "D_minus":
        scGear.singleServo(15, -1, 1)
    elif command_input == "DS":
        scGear.stopWiggle()
        
    # elif command_input == "E_add":
    #     scGear.singleServo(4, 1, 1) # (servoPort, direction, speed)
    # elif command_input == "E_minus":
    #     scGear.singleServo(4, -1, 1)
    # elif command_input == "ES":
    #     scGear.stopWiggle()

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

# 摇杆初始化
# Joystick initialization.

# 读取摇杆值
# read joystick value.

# 检测树莓派是否连接到网络
# Check if the Raspberry Pi is connected to the network.
def WiFi_check():
    try:
        s =socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(("1.1.1.1",80))
        ipaddr_check=s.getsockname()[0]
        s.close()
        print(ipaddr_check)
    except:
        ap_threading=threading.Thread(target=ap_thread)   #Define a thread for data receiving
        ap_threading.setDaemon(True)                          #'True' means it is a front thread,it would close when the mainloop() closes
        ap_threading.start()                                  #Thread starts
        print("Raspberry Pi WiFi Turn On!")
        print("IP: 192.168.12.1")

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

    while True:
        WiFi_check()
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

    
        