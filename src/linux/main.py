import os

os.system("v4l2-ctl -d /dev/video2 -c focus_auto=0")
os.system("v4l2-ctl -d /dev/video2 -c focus_absolute=255")
os.system("v4l2-ctl -d /dev/video2 -c focus_absolute=0")
os.system("v4l2-ctl -d /dev/video2 -c focus_absolute=80")
os.system("v4l2-ctl -d /dev/video2 -c focus_auto=1")
