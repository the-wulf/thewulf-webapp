# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from thewulfcms.models import *
from datetime import *
import mad
import contextlib
import os.path
import wave
import contextlib
import math
from tinytag import TinyTag
# <codecell>

def copland_scrape():
    event_list = Event.objects.filter(start_date__gt=date(2013, 11, 22)).order_by('start_date')
    event_list = event_list.reverse()
    text_file = open("copland.txt", "w")
    fstring = ""
    for e in event_list:
	print(e.name)
        fstring += e.start_date.strftime("%m.%d.%y") + ": " + e.name
        program = Program.objects.select_related().filter(event = e).order_by('position')
        performers = Performer.objects.select_related().filter(event = e).order_by('position')
        recs = EventAudioRecording.objects.select_related().filter(event = e).order_by('position')
        dur = ""
	for i in range(len(program)):
            work = program[i].works.all()[0]
            if len(recs) > 0 and os.path.isfile(recs[i].compressed_master_recording.path):
                #mf = mad.MadFile(recs[i].compressed_master_recording.path)
                #dur = int(mf.total_time() / 1000)
                #dur = str(timedelta(seconds=dur))
		#fname = recs[i].uncompressed_master_recording.path
		#print(fname)
		#with contextlib.closing(wave.open(fname,'r')) as f:
		#    frames = f.getnframes()
    		#    rate = f.getframerate()
    		#    duration = math.floor(frames / float(rate))
		#    minutes, seconds = divmod(duration, 60)
		#    hours, minutes = divmod(minutes, 60)
		#    dur = str(hours) + ":" + str(minutes) + ":" + str(seconds)
		tag = TinyTag.get(recs[i].compressed_master_recording.path)
		duration = tag.duration
		print(duration)
		minutes, seconds = divmod(duration, 60)
                hours, minutes = divmod(minutes, 60)
                dur = str(int(hours)) + ":" + str(int(minutes)) + ":" + str(int(seconds))

            else:
                dur = "????"
            fstring += "\n"+work.name + " by " + work.authors.all()[0].name + "* - " + dur
        if len(performers) > 0:
            fstring += "\nperformers: "
            for p in performers:
                fstring += p.performer.name + " - "
                for i in p.instruments.all():
                    fstring += i.name + ", "
                fstring = fstring[:-2]
                fstring += "; "
            fstring = fstring[:-2]
        fstring += "\n\n"
    text_file.write(fstring.encode('utf-8'))
    text_file.close()
    


