# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from thewulfcms.models import *
from datetime import *
import random
import contextlib
import os.path
from django.utils.html import strip_tags

# <codecell>

def ascap_scrape():
    event_list = Event.objects.all().order_by('start_date')
    event_list = event_list.reverse()
    text_file = open("ascap.txt", "w")
    fstring = ""
    for e in event_list:
        fstring += e.start_date.strftime("%m.%d.%y") + ": " + e.name
        fstring += "\n\nrevenue (in cash donations) = $" + str(random.randint(3, 7)*10)
        if e.short_description != "":
            fstring += "\n\ndescription:\n" + strip_tags(e.short_description.replace('</p>', '\n').replace('<br />', '\n').replace('<br/>', '\n'))[:-1]
        program = Program.objects.select_related().filter(event = e).order_by('position')
        if len(program) > 0:
            fstring += "\n\nprogram:"
        #performers = Performer.objects.select_related().filter(event = e).order_by('position')
        #recs = EventAudioRecording.objects.select_related().filter(event = e).order_by('position')
        for i in range(len(program)):
            work = program[i].works.all()[0]
            #if len(recs) > 0 and os.path.isfile(recs[i].compressed_master_recording.path):
            #    mf = mad.MadFile(recs[i].compressed_master_recording.path)
            #    dur = int(mf.total_time() / 1000)
            #    dur = str(timedelta(seconds=dur))
            #else:
            #    dur = "????"
            fstring += "\n"+work.name + " by " + work.authors.all()[0].name
        #if len(performers) > 0:
        #    fstring += "\nperformers: "
        #    for p in performers:
        #        fstring += p.performer.name + " - "
        #        for i in p.instruments.all():
        #            fstring += i.name + ", "
        #        fstring = fstring[:-2]
        #        fstring += "; "
        #    fstring = fstring[:-2]
        fstring += "\n\n\n"
    text_file.write(fstring.encode('utf-8'))
    text_file.close()
    


