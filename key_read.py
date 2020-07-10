#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import getopt
import string
from evdev import InputDevice, ecodes
from select import select
import vlc
import os.path
import time
import pickle
import re
import subprocess
#pip3 install moviepy - для определения размеров видео
#sudo apt-get install libatlas-base-dev

#pip3 install FFProbe

#pip3 install libmediainfo
#sudo apt-get install libmediainfo0v5

#sudo apt install python3-opencv
#sudo apt-get install libatlas-base-dev
#sudo apt-get install libjasper-dev
#sudo apt-get install libqtgui4
#sudo apt-get install python3-pyqt5
#pip3 install opencv-python
# https://github.com/EdjeElectronics/TensorFlow-Object-Detection-on-the-Raspberry-Pi/issues/67
# vi .bashrc (or nano .bashrc under root)
#add：export LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1
#exit with save file.
# source .bashrc

#FLASH_PATH='/media/pi/Transcend'
#FLASH_PATH='/media/pi/UUI'
FLASH_PATH='/media/pi/ASUS_HDD'

from pymediainfo import MediaInfo
#import cv2
















# Initialize table for IR remote
result = subprocess.run(["sudo", "ir-keytable", "-c", "-p", "nec", "-w", "/lib/udev/rc_keymaps/myremote.toml"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)

NAME = os.path.basename(sys.argv[0])

keys = ".^1234567890....qwertzuiop....asdfghjkl.....yxcvbnm......................."

#
# Local functions
#

def error(*objs):
    print(NAME, ": ", *objs, file = sys.stderr)

def usage():
    print("usage: ", NAME, " [-h] <inputdev>", file = sys.stderr)
    sys.exit(2);

#
# Main
#

try:
        opts, args = getopt.getopt(sys.argv[1:], "h",
                        ["help"])
except getopt.GetoptError as err:
        # Print help information and exit:
        error(str(err))
        usage()

for o, a in opts:
        if o in ("-h", "--help"):
                usage()
        else:
                assert False, "unhandled option"

# Check command line
if len(args) < 1:
    usage()






# Try to open the input device
try:
    dev = InputDevice(args[0])
except:
    error("invalid input device", args[0])
    sys.exit(1);

#Now read data from the input device printing only letters and numbers














class TV_show:
    def __init__(self, name, duration=0):
        self.name=name
        if duration:
            self.duration=duration
        else:
            self.duration=self.get_duration()

    def get_duration(self):
        #video = cv2.VideoCapture(self.name)
        
        #duration = video.get(cv2.CAP_PROP_POS_MSEC)
        #frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
        #fps = video.get(cv2.CAP_PROP_FPS)
        #return frame_count/fps
        #return duration, frame_count
        media_info = MediaInfo.parse(self.name)
        return float(media_info.tracks[0].duration)
        #result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
        #                                          "format=duration", "-of",
        #                                          "default=noprint_wrappers=1:nokey=1", self.name],
        #stdout=subprocess.PIPE,
        #stderr=subprocess.STDOUT)
        #return float(result.stdout.splitlines()[-1])

    def __str__(self):
        return str(self.name) + " : " + str(self.duration)


class TV_channel:
    def __init__(self, channel):
        self.channel=channel
        self.tv_shows=[]
        self.duration=0
        self.rewind=0

    def add_show(self, program, duration=0):
        try:
            if duration:
                show = TV_show(program, duration)
            else:
                show = TV_show(program)
        except Exception as e:
            print(e)
        self.tv_shows.append(show)
        self.duration+=show.duration

    def __getitem__(self, index):
        return self.tv_shows[index]

    def __str__(self):
        return str([ str(show) for show in self.tv_shows ])


class TV:
    def __init__(self):
        self.channels=[]
        for ch in range(10):
            self.channels.append(TV_channel(ch))
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        self.feh_photo_instance=None

    def add_flash_drive(self, drive_path):
        while (not os.path.exists(drive_path)):
            print("sleep 1s")
            time.sleep(1)
        print("hdd is ready")
        time.sleep(1)

        black_background_feh = subprocess.Popen(["feh", "-Y", "-F", "/home/pi/grandma_TV/black_background.jpg"],
          stdout=subprocess.PIPE,
          stderr=subprocess.STDOUT ,
          env={"DISPLAY" : ":0", "XDG_RUNTIME_DIR" : "/run/user/1000"}
        )

        durations={}
        if os.path.isfile(drive_path+'/durations.pickle'):
            with open(drive_path+'/durations.pickle', 'rb') as f:
                durations = pickle.load(f)
        print("pickle loaded!")
        files_in_path = [os.path.join(path, name) for path, subdirs, files in os.walk(drive_path) for name in files]
        videos_in_flash = [file_path for file_path in files_in_path if (file_path.endswith(".mkv") or file_path.endswith(".AVI") or file_path.endswith(".avi") or file_path.endswith(".mpg") or file_path.endswith(".m4v") or file_path.endswith(".ts")) ]
        photos_in_flash = [file_path for file_path in files_in_path if (file_path.endswith(".jpg") or file_path.endswith(".JPG"))] 
        for video in videos_in_flash:
            try:
                channel_number = int(video[len(drive_path+'/Program_')])
                if video in durations:
                    tv.add_TV_show(channel_number, video, durations[video])
                else:
                    print("add tvshow: " + str(video))
                    tv.add_TV_show(channel_number, video)
                    last_show=self.channels[channel_number].tv_shows[-1]
                    durations[last_show.name] = last_show.duration
                    with open(drive_path+'/durations.pickle', 'wb') as f:
                        pickle.dump(durations, f)
            except Exception as e:
                print(video)
                print(e)
                continue
        for photo in photos_in_flash:
            try:
                channel_number = int(photo[len(drive_path+'/Program_')])
                tv.add_TV_show(channel_number, photo, 10*1000)
            except:
                continue
 

    def add_TV_show(self, channel, program, duration=0):
        if duration:
            self.channels[channel].add_show(program, duration)
        else:
            self.channels[channel].add_show(program)

    def show_time_as_str(self, ms_time):
        #return (str(int(ms_time/1000/60/60))+':'+ str(int(ms_time/1000/60%60)))
        return '{:d}:{:02d}'.format(int(ms_time/1000/60/60), int(ms_time/1000/60%60))
        

    def show_title(self, timeout=0):
        m = vlc.VideoMarqueeOption
        self.player.video_set_marquee_int(m.Enable, 1)
        w, h = self.player.video_get_size(0)
        self.player.video_set_marquee_int(m.Size, int((h/1080)*(1080/7)))  # pixels
        self.player.video_set_marquee_int(m.Position, vlc.Position.Bottom)
        self.player.video_set_marquee_int(m.Opacity, 255)  # 0-255
        self.player.video_set_marquee_int(m.Timeout, timeout)  # millisec, 0==forever
        self.player.video_set_marquee_int(m.Refresh, 1000)  # millisec (or sec?)

        channel_time=int( (time.time()*1000 + self.channels[self.active_channel].rewind) % self.channels[self.active_channel].duration )
        show_number=0
        while show_number != self.active_show:
            channel_time -= self.channels[self.active_channel][show_number].duration 
            show_number += 1

        channel_time_int=int(channel_time)
        show_elapsed_time_str=self.show_time_as_str(channel_time_int)
        show_duration_time_str=self.show_time_as_str(self.channels[self.active_channel][self.active_show].duration)
        show_title_match = re.search('/media/pi/.*/Program_.?/(.+?)(.mkv|.ts|.avi|.AVI|.mpg|.m4v)', self.channels[self.active_channel][self.active_show].name)
        if show_title_match:
            show_title = show_title_match.group(1)
            show_title_pretty = show_title.replace('/','\n')
            if (self.channels[self.active_channel][self.active_show].duration == 10*1000):
               self.player.video_set_marquee_string(m.Text, show_title_pretty)
            else:
               self.player.video_set_marquee_string(m.Text, show_title_pretty + ' \n' + 'Прошло ' + show_elapsed_time_str + ' из ' + show_duration_time_str)

    def hide_title(self):
        m = vlc.VideoMarqueeOption
        self.player.video_set_marquee_int(m.Enable, 0)

    def play(self, channel=''):
        if channel != '':
            if not len(self.channels[channel].tv_shows):
                 return
            self.active_channel = channel
        else:
            channel = self.active_channel

        self.hide_title()
        channel_time=int( (time.time()*1000 + self.channels[channel].rewind) % self.channels[channel].duration )
        show_number=0
        while True:
            if self.channels[channel][show_number].duration < channel_time:
                channel_time -= self.channels[channel][show_number].duration 
                show_number += 1
            else:
                break
        self.active_show = show_number
        channel_time_int=int(channel_time)

        if (self.feh_photo_instance):
            self.feh_photo_instance.kill()
        file_name=self.channels[channel][show_number].name
        if (file_name.endswith(".JPG") or (file_name.endswith(".jpg"))):
            self.player.stop()

            self.feh_photo_instance = subprocess.Popen(["feh", "-Y", "-F", file_name],
                  stdout=subprocess.PIPE,
                  stderr=subprocess.STDOUT ,
                  env={"DISPLAY" : ":0", "XDG_RUNTIME_DIR" : "/run/user/1000"}
            )
            print(self.channels[channel][show_number].name)
            self.photo_time=time.time()
        else:
            Media = self.vlc_instance.media_new( self.channels[channel][show_number].name )
            print(self.channels[channel][show_number].name)
            self.player.set_media(Media)
            self.player.set_fullscreen(True)
            self.player.play()
            self.player.set_time( int( channel_time_int) )
            time.sleep(1)
            self.player.video_set_spu(-1)

    def next_channel(self):
        if (self.active_channel==9):
            self.play(0)
        else:
            self.play(self.active_channel+1)

    def previous_channel(self):
        if (self.active_channel==0):
            self.play(9)
        else:
            self.play(self.active_channel-1)

    def play_ended(self):
        file_name=self.channels[self.active_channel][self.active_show].name
        if (file_name.endswith(".JPG") or (file_name.endswith(".jpg"))):
            return (time.time() > (self.photo_time + 10))
        else:
            return self.player.get_state() == vlc.State.Ended

    def turn_off(self):
        self.player.stop()
        self.player.release()
        subprocess.run(["sudo", "sync"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        subprocess.run(["sudo", "eject", "/dev/sda" ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        subprocess.run(["sudo", "udisksctl", "unmount", "-b", "/dev/sda1"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        subprocess.run(["sudo", "udisksctl", "power-off", "-b", "/dev/sda"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #time.sleep(5)
        subprocess.run(["sudo", "poweroff"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


    def rewind_show(self):
        channel_time=int( (time.time()*1000 + self.channels[self.active_channel].rewind) % self.channels[self.active_channel].duration )
        show_number=0
        while show_number != self.active_show:
            channel_time -= self.channels[self.active_channel][show_number].duration 
            show_number += 1

        channel_time_int=int(channel_time)

        self.channels[self.active_channel].rewind += (self.channels[self.active_channel][self.active_show].duration-channel_time_int)
        self.channels[self.active_channel].rewind += 500 # jump a little futher
        self.play()

    def rewind_show_back(self):
        channel_time=int( (time.time()*1000 + self.channels[self.active_channel].rewind) % self.channels[self.active_channel].duration )
        show_number=0
        while show_number != self.active_show:
            channel_time -= self.channels[self.active_channel][show_number].duration 
            show_number += 1

        channel_time_int=int(channel_time)
        if (channel_time_int < 5000):
            if self.active_show == 0:
                previous_show_number=len(self.channels[self.active_channel].tv_shows)-1
            else:
                previous_show_number=self.active_show-1
            self.channels[self.active_channel].rewind -= (channel_time_int + self.channels[self.active_channel][previous_show_number].duration)
        else:
            self.channels[self.active_channel].rewind -= channel_time_int

        self.channels[self.active_channel].rewind += 500 # jump a little futher
        self.play()




tv = TV()
tv.add_flash_drive(FLASH_PATH)

tv.play(1)

print("TV is on!")



import signal
import sys

def signal_handler(signal, frame):
  # your code here
  if (tv.feh_photo_instance):
      tv.feh_photo_instance.terminate()
  if (black_background_feh):
      black_background_feh.terminate()
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)





while True:
    r, w, x = select([dev], [], [], 1)

    if tv.play_ended():
        tv.play()

    if not r:
        continue
    for event in dev.read():
        # Print key pressed events only
        if event.type == ecodes.EV_KEY and event.value == 1:
            #print(hex(event.code))
            if event.code == 0x201:
                print("Channel was switched to 1")
                tv.play(1)
            if event.code == 0x202:
                print("Channel was switched to 2")
                tv.play(2)
            if event.code == 0x203:
                print("Channel was switched to 3")
                tv.play(3)
            if event.code == 0x204:
                print("Channel was switched to 4")
                tv.play(4)
            if event.code == 0x205:
                print("Channel was switched to 5")
                tv.play(5)
            if event.code == 0x206:
                print("Channel was switched to 6")
                tv.play(6)
            if event.code == 0x207:
                print("Channel was switched to 7")
                tv.play(7)
            if event.code == 0x208:
                print("Channel was switched to 8")
                tv.play(8)
            if event.code == 0x209:
                print("Channel was switched to 9")
                tv.play(9)
            if event.code == 0x200:
                print("Channel was switched to 0")
                tv.play(0)
            if event.code == 0x192:
                tv.next_channel()
            if event.code == 0x193:
                tv.previous_channel()
            if event.code == 0x69:
                tv.rewind_show_back()
            if event.code == 0x6a:
                tv.rewind_show()
            if event.code == 0x67:
                tv.show_title(0)
            if event.code == 0x6c:
                tv.hide_title()
            if event.code == 0x160:
                print("TV is off")
                tv.turn_off() 

