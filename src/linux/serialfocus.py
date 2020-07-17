import serial
import os
import time

focus_auto = 0
dev = "/dev/video2"
ant = 0
absolute_focus = 0
cmd = None

line = None
with serial.Serial('/dev/ttyACM0', 115200) as ser:
    while True:
        line = ser.readline()   # read a '\n' terminated line
        print(line)
        if line == b'Button pressed.\r\n':
            print("auto")
            cmd = "v4l2-ctl -d " + dev + " -c focus_auto=" + str(focus_auto)
            if focus_auto == 0:
                focus_auto = 1
            else:
               focus_auto = 0
        elif focus_auto == 0:
            print("Autofoco activado, no manual")
        else:
            if int(line) < ant:
                absolute_focus -= 5
            else:
                absolute_focus += 5
            ant = int(line)
            if absolute_focus <= 0:
                print("Límite de foco alcanzado")
                absolute_focus = 0
            elif absolute_focus >= 255:
                print("Límite de foco alcanzado")
                absolute_focus = 255
            cmd = "v4l2-ctl -d " + dev + " -c focus_absolute=" + str(absolute_focus)
        if cmd != None:
            print(cmd)
            os.system(cmd)
