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
    
    help = "fix file path"

    def handle(self, *args, **options):
        for arg in args:
            [year,month,day] = arg.split("_")
            event = Event.objects.get(start_date__year = year, start_date__month = month, start_date__day = day)
            for rec in EventAudioRecording.objects.filter(event = event):
                rec.compressed_master_recording.name = rec.compressed_master_recording.name.replace("mp3", "ogg")
                rec.save()