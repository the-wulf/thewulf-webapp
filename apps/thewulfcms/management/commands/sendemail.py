from django.core.management.base import BaseCommand, CommandError
from django.template import Context, loader, Library
from django.core.mail import send_mail
from django.template.loader import render_to_string
from thewulf.thewulfcms.models import *
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from datetime import *

class Command(BaseCommand):
    
    def handle(self, *args, **options):
                
        fundraiser = Event.objects.get(name='the wulf. fundraiser')
        upcoming_event_list = Event.objects.filter(start_date__gte=datetime.now()).order_by('start_date')
        venue = AbstractProfile.objects.select_subclasses().get(name='the wulf.')
             
        html_content = render_to_string('event_email.html', {'venue': venue, 'upcoming_event_list': upcoming_event_list, 'fundraiser': fundraiser})
        text_part = strip_tags(html_content)
        
        msg = EmailMultiAlternatives('Subject here', text_part, 'info@thewulf.org',['info@thewulf.org','events@lists.thewulf.org'])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
