from django.core.management.base import BaseCommand, CommandError
from django.template import Context, loader, Library
from thewulf.thewulfcms.models import *
import os
import re
from django.contrib.auth.models import User, Group
from datetime import *
from optparse import make_option
import subprocess

class Command(BaseCommand):
    
    help = "compress the audio"

    def handle(self, *args, **options):
            audio_dur_check(args[0], args[1])
            
    
def audio_dur_check(top_folder, date_string):
    command = ''
    for root,dirs,files in os.walk(top_folder): #walk through the specified directory
        for form in files:
            if form.endswith(date_string + ".txt"): #find all .txt files
                data = open(os.path.join(root, form))
                line = data.readline() #for line in data
                #date_string = form.split('.')[0]
                event_folder = '/home/mwinter80/thewulf.org/public/media/events/' + date_string
                master_uncompressed_folder = event_folder + '/uncompressed_mastered_recordings/'
                
                command = "#!/bin/bash\n\n"
                command = command + "export PATH=\"$HOME/bin:$PATH\"\n\n"
                command = command + 'echo \"\"\n'
                command = command + "echo " + date_string + "\n"
                command = command + 'echo \"\"\n'
                command = command + "echo " + os.path.join(root, form) + "\n"
                track_count = 0
                startTime = 0
                
                while line:
                    
                    if 'Start_Time:' in line:
                        track_count += 1
                        startTime = re.search('Start_Time: (.*)\'\'',line)
                        startTime = startTime.group(1)
                        prefix = '0'
                        if track_count > 9:
                            prefix = ''
                        startTime = startTime.split("\'")
                        
                    
                    #gets end time of piece
                    if 'End_Time:' in line:
                        if startTime[0] != "X":
                            startTime = int(startTime[0])*60+int(startTime[1])
                            command = command + 'echo \"\"\n'
                            command = command + "echo " + prefix + str(track_count) + ".wav\n"
 
                            endTime = re.search('End_Time: (.*)\'\'',line)
                            endTime = endTime.group(1)
                            endTime = endTime.split("\'")
                            if endTime[0] != "X":
                                endTime = int(endTime[0])*60+int(endTime[1])
                                dur = endTime - startTime
                                dur = str(timedelta(seconds=dur))
                                command = command + "echo "+ dur + "\n"
                                rec_path = master_uncompressed_folder + prefix + str(track_count) + ".wav"
                                command = command + "if test -e " + rec_path + "; "
                                command = command + "then soxi -d " + rec_path + "; "
                                command = command + "else echo wav definitely missing; fi\n"
                            else:
                                command = command + "echo wav likely missing\n"
                        else:
                            command = command + "echo wav likely missing\n"
                                
                    line = data.readline()
                    
                command = command + 'echo \"\"\n'
                command = command + 'echo \"\"\n'
                command = command + "\n\n"
                
    f = open('/home/mwinter80/scripts/tmp/check_audio.sh', 'w')
    f.write(command)
    f.close()
    subprocess.call(['/home/mwinter80/scripts/tmp/check_audio.sh'])