from django.core.management.base import BaseCommand, CommandError
from django.template import Context, loader, Library
#from thewulf.thewulfcms.models import *
import os
import re
from django.contrib.auth.models import User, Group
from datetime import *
from optparse import make_option
import subprocess

class Command(BaseCommand):
    
    help = "chop the audio"
    
    def handle(self, *args, **options):
        card_scrape_chopper(args[0], args[1])


def card_scrape_chopper(top_folder, date_string):
    print "fjdska;fmdsakfd;sanfidsafjdsaf;dsafjdias;fdajsfdisa;j"
    command = ''
    for root,dirs,files in os.walk(top_folder): #walk through the specified directory
        print root, dirs, files
        for form in files:
            if form.endswith(date_string + ".txt"): #find all .txt files
                data = open(os.path.join(root, form))
                line = data.readline() #for line in data
                #date_string = form.split('.')[0]
                event_folder = '/home/mwinter80/thewulf.org/public/media/events/' + date_string
                raw_folder = event_folder + '/raw_audio_recordings/' 
                master_uncompressed_folder = event_folder + '/uncompressed_mastered_recordings/'
                master_compressed_folder = event_folder + '/compressed_mastered_recordings/'
                video_folder = event_folder + '/videos/'
                zipfile = date_string + ".zip"
                
                command = "#!/bin/bash\n\n"
                command = command + "export PATH=\"$HOME/bin:$PATH\"\n"
                command = command + "cd " + raw_folder + "\n" 
                #command = command + "jar xvf " + zipfile + "\n"
                #command = command + "cd wulf_archive_autoconcat\n"
                #command = command + "cd " + zipfile.split('.')[0] + "\n"
                #command = command + "sox -M 1.wav 2.wav stereo.wav\n"
                
                command = command + "ffmpeg -i " + date_string + ".mov -vn -acodec copy stereo.wav\n"
                
                command = command + "mkdir " + master_uncompressed_folder + "\n" 
                command = command + "mkdir " + master_compressed_folder + "\n" 
                command = command + "mkdir " + video_folder + "\n" 
                track_count = 0
                
                mov_command = ""
                prefix = ""
                
                while line:
                    
                    if 'Start_Time:' in line:
                        track_count += 1
                        startTime = re.search('Start_Time: (.*)\'\'',line)
                        if startTime == None:
                            startTime = re.search('Start_Time: \d\d:\d\d:\d\d',line).group(0)
                            startTime = startTime.replace('Start_Time: ', '')
                        else:
                            startTime = startTime.group(1)
                        prefix = '0'
                        if track_count > 9:
                            prefix = ''
                        
                        command = command + "sox --temp /home/mwinter80/tmp_sox --norm=-.05 stereo.wav " + master_uncompressed_folder + prefix + str(track_count) + ".wav trim =" + startTime.replace("\'", ":") + " "
                        mov_command =  "ffmpeg -i " + date_string + ".mov -ss " + startTime.replace("\'", ":") + " "
                        
                    
                    #gets end time of piece
                    if 'End_Time:' in line:
                        endTime = re.search('End_Time: (.*)\'\'',line)
                        if endTime == None:
                            endTime = re.search('End_Time: \d\d:\d\d:\d\d',line).group(0)
                            endTime = endTime.replace('End_Time: ', '')
                        else:
                            endTime = endTime.group(1)
                        
                        command = command + "=" + endTime.replace("\'", ":") + "\n"
                        #command = command + "sox " + master_uncompressed_folder + prefix + str(track_count) + ".wav " + master_compressed_folder + prefix + str(track_count) + ".ogg\n"
                        mov_command = mov_command + "-to " + endTime.replace("\'", ":") + " -codec copy " + video_folder + prefix + str(track_count) + ".mov\n"
                        command = command + mov_command
                        
                    line = data.readline()
                    
                command = command + "rm -rf " + raw_folder + "wulf_archive_autoconcat\n"
                command = command + "rm -rf " + raw_folder + "stub\n"
                command = command + "rm -rf " + raw_folder + date_string + "\n"
                command = command + '\n\n'
                
    f = open('/home/mwinter80/scripts/tmp/chop_audio.sh', 'w')
    #print command
    f.write(command)
    f.close()
    subprocess.call(['/home/mwinter80/scripts/tmp/chop_audio.sh'])
