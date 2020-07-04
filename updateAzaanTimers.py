#!/usr/bin/env python

import datetime
import time
import sys
import random

sys.path.insert(0, '/home/pi/adhan/crontab')

from praytimes import PrayTimes
PT = PrayTimes() 

from crontab import CronTab
system_cron = CronTab(user='pi')

now = datetime.datetime.now()
strUpdateCommand = 'python /home/pi/adhan/updateAzaanTimers.py >> /home/pi/adhan/adhan.log 2>&1'
strKillCommand = 'sudo killall /usr/bin/omxplayer.bin;sudo killall omxplayer'
strClearLogsCommand = 'truncate -s 0 /home/pi/adhan/adhan.log 2>&1'
strJobComment = 'rpiAdhanClockJob'

#Set latitude and longitude here
#--------------------
lat = 47.75732
long = -122.24401

#Set calculation method, utcOffset and dst here
#By default system timezone will be used
#--------------------
PT.setMethod('ISNA')
utcOffset = -(time.timezone/3600)
isDst = time.localtime().tm_isdst


#HELPER FUNCTIONS
#---------------------------------
#---------------------------------
#Function to add azaan time to cron
def get_adhan_filename(is_fajr):
    if is_fajr:
        adhans = [
	    "Adhan-fajr.mp3",
	    "Adhan-Mansour-Zahrani-fajr.mp4",
	]
    else:
        adhans = [
            "Adhan-Makkah2.mp3",
            "Adhan-Mishary-Rashid-Al-Afasy.mp3",
            "Adhan-Turkish.mp3",
            "Adhan-Mansour-Zahrani.mp3",
	    "Adhan-Junaid-Jamshed-Makkah.mov",
            "Adhan-Junaid-Jamshed-Mississauga.m4a",
        ]
    return random.choice(adhans)

def get_adhan_cmd(is_fajr = False):
    return 'omxplayer -o local /home/pi/adhan/{} > /dev/null 2>&1'.format(get_adhan_filename(is_fajr))

def addAzaanTime (strPrayerName, strPrayerTime, objCronTab, strCommand):
  job = objCronTab.new(command=strCommand,comment=strPrayerName)  
  timeArr = strPrayerTime.split(':')
  hour = timeArr[0]
  min = timeArr[1]
  job.minute.on(int(min))
  job.hour.on(int(hour))
  job.set_comment(strJobComment)
  print job
  return

def addUpdateCronJob (objCronTab, strCommand):
  job = objCronTab.new(command=strCommand)
  job.minute.on(15)
  job.hour.on(3)
  job.set_comment(strJobComment)
  print job
  return

def addClearLogsCronJob (objCronTab, strCommand):
  job = objCronTab.new(command=strCommand)
  job.day.on(1)
  job.minute.on(0)
  job.hour.on(0)
  job.set_comment(strJobComment)
  print job
  return
#---------------------------------
#---------------------------------
#HELPER FUNCTIONS END

# Remove existing jobs created by this script
system_cron.remove_all(comment=strJobComment)

# Calculate prayer times
times = PT.getTimes((now.year,now.month,now.day), (lat, long), utcOffset, isDst) 
print times['sunrise']
print times['dhuhr']
print times['asr']
print times['maghrib']
print times['isha']

# Add times to crontab
addAzaanTime('sunrise',times['sunrise'],system_cron,get_adhan_cmd(True))
addAzaanTime('dhuhr',times['dhuhr'],system_cron,get_adhan_cmd())
addAzaanTime('asr',times['asr'],system_cron,get_adhan_cmd())
addAzaanTime('maghrib',times['maghrib'],system_cron,get_adhan_cmd())
addAzaanTime('isha',times['isha'],system_cron,get_adhan_cmd())

# Run this script again overnight
addUpdateCronJob(system_cron, strUpdateCommand)
addUpdateCronJob(system_cron, strKillCommand)

# Clear the logs every month
addClearLogsCronJob(system_cron,strClearLogsCommand)

system_cron.write_to_user(user='pi')
print 'Script execution finished at: ' + str(now)
