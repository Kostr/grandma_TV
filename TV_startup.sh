#!/bin/bash

echo "TV_startuppp" > /home/pi/my_startup_log.txt 
python3 /home/pi/grandma_TV/key_read.py /dev/input/event0 > /home/pi/mylog.txt 2> /home/pi/mylog.err 
