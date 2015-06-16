from thewulfcms.models import *
from datetime import *
import urllib
import re
from django.core.files.storage import default_storage
#import mad

def audio_check():
    events=Event.objects.all().order_by('start_date')
    text_file = open("audio_check/audio_check.txt", "w")
    fin_string=""
    for e in events:
        date = e.start_date.strftime("%Y_%m_%d" )
        name = e.name
        fin_string += date + "::" + name + "\n"
        raw = e.raw_audio_recording
        if bool(raw):
            url = raw.url
            f = urllib.urlopen(url)
            if f.code != 200:
                fin_string += "\traw audio recording file does not exist for " + url +"\n"
            else:
                recs=e.eventaudiorecording_set.all()
                if len(recs) == 0:
                    fin_string += "\thas raw audio recording file but no individual recordings\n"
                else:
                    for r in recs:
                        uncompressed = r.uncompressed_master_recording
                        if bool(uncompressed):
                            url = uncompressed.url
                            f = urllib.urlopen(url)
                            if f.code != 200:
                                fin_string += "\tposition " + str(r.position) + ": uncompressed file does not exist for " + url +"\n"
                        else:
                            fin_string += date + "\tposition " + str(r.position) + ": has no uncompressed file url\n"
                    for r in recs:
                        compressed = r.compressed_master_recording
                        if bool(compressed):
                            url = compressed.url
                            f = urllib.urlopen(url)
                            if f.code != 200:
                                fin_string += "\tposition " + str(r.position) + ": compressed file does not exist for " + url +"\n"
                        else:
                            fin_string += date + "\tposition " + str(r.position) + ": has no compressed file url\n"
        else:
            fin_string += "\thas no raw audio recording url\n"
    text_file.write(fin_string.encode('utf-8'))
    text_file.close()
    
def audio_check_single(namestring):
    events=Event.objects.filter(name = namestring)
    text_file = open("audio_check/audio_check_single.txt", "w")
    fin_string=""
    for e in events:
        date = e.start_date.strftime("%Y_%m_%d" )
        name = e.name
        fin_string += date + "::" + name + "\n"
        raw = e.raw_audio_recording
        if bool(raw):
            url = raw.url
            f = urllib.urlopen(url)
            if f.code != 200:
                fin_string += "\traw audio recording file does not exist for " + url +"\n"
            else:
                recs=e.eventaudiorecording_set.all()
                if len(recs) == 0:
                    fin_string += "\thas raw audio recording file but no individual recordings\n"
                else:
                    for r in recs:
                        uncompressed = r.uncompressed_master_recording
                        if bool(uncompressed):
                            url = uncompressed.url
                            f = urllib.urlopen(url)
                            if f.code != 200:
                                fin_string += "\tposition " + str(r.position) + ": uncompressed file does not exist for " + url +"\n"
                        else:
                            fin_string += date + "\tposition " + str(r.position) + ": has no uncompressed file url\n"
                    for r in recs:
                        compressed = r.compressed_master_recording
                        if bool(compressed):
                            url = compressed.url
                            f = urllib.urlopen(url)
                            if f.code != 200:
                                fin_string += "\tposition " + str(r.position) + ": compressed file does not exist for " + url +"\n"
                        else:
                            fin_string += date + "\tposition " + str(r.position) + ": has no compressed file url\n"
        else:
            fin_string += "\thas no raw audio recording url\n"
    text_file.write(fin_string.encode('utf-8'))
    text_file.close()
    
def audio_dur_check(top_folder):
    command = ''
    for root,dirs,files in os.walk(top_folder): #walk through the specified directory
        for form in files:
            if form.endswith(".txt"): #find all .txt files
                data = open(os.path.join(root, form))
                line = data.readline() #for line in data
                date_string = form.split('.')[0]
                event_folder = '/home/mwinter80/thewulf.org/public/media/events/' + date_string
                master_uncompressed_folder = event_folder + '/uncompressed_mastered_recordings/'
                
                command = command + "echo " + date_string + " >> audio_dur_test.log\n"
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
                            command = command + "echo " + prefix + str(track_count) + ".wav >> audio_dur_test.log\n"
 
                            endTime = re.search('End_Time: (.*)\'\'',line)
                            endTime = endTime.group(1)
                            endTime = endTime.split("\'")
                            if endTime[0] != "X":
                                endTime = int(endTime[0])*60+int(endTime[1])
                                dur = endTime - startTime
                                dur = str(timedelta(seconds=dur))
                                command = command + "echo "+ dur + " >> audio_dur_test.log\n"
                                rec_path = master_uncompressed_folder + prefix + str(track_count) + ".wav"
                                command = command + "if test -e " + rec_path + "; "
                                command = command + "then soxi -d " + rec_path + " >> audio_dur_test.log; "
                                command = command + "else echo wav definitely missing >> audio_dur_test.log; fi\n"
                            else:
                                command = command + "echo wav likely missing >> audio_dur_test.log\n"
                        else:
                            command = command + "echo wav likely missing >> audio_dur_test.log\n"
                                
                    line = data.readline()
                    
                command = command + 'echo \"\" >> audio_dur_test.log\n'
                command = command + 'echo \"\" >> audio_dur_test.log\n'
                command = command + "\n\n"
                
    f = open('audio_dur_check.txt', 'w')
    f.write(command)
    f.close()