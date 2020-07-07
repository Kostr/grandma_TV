#!/bin/bash

sudo pkill python3
sudo echo "Shutdown!"
if [ -d "/media/pi/ASUS_HDD" ]; then
	sudo sync
	sudo umount /media/pi/ASUS_HDD
	sudo eject /dev/sda
	sudo udisksctl unmount -b /dev/sda1
	sudo udisksctl power-off -b /dev/sda
	sudo echo "Umount HDD" >> /home/pi/my_shutdown_log.txt
else
	sudo echo "No HDD is present!" >> /home/pi/my_shutdown_log.txt
fi

