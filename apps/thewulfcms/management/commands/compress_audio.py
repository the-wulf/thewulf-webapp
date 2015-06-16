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
        for arg in args:
            subprocess.call(['/home/mwinter80/scripts/compress_audio.sh', arg])