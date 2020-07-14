#!/bin/bash

echo "TV_startuppp" > /home/pi/my_startup_log.txt
export DISPLAY=:0
unclutter -idle 0 &
#feh --fullscreen --hide-pointer /home/pi/grandma_TV/black_background.jpg > /home/pi/feh.log & 
python3 /home/pi/grandma_TV/key_read.py /dev/input/event0 > /home/pi/mylog.txt 2> /home/pi/mylog.err 
