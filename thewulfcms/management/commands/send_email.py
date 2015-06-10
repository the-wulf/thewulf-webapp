from django.core.management.base import BaseCommand, CommandError
from django.template import Context, loader, Library
from django.core.mail import send_mail
from django.template.loader import render_to_string
from thewulf.thewulfcms.models import *
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from datetime import *
from BeautifulSoup import BeautifulSoup
from django.conf import settings
from email.MIMEImage import MIMEImage
import urllib, cStringIO

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        
        print(settings.EMAIL_HOST)
                
        upcoming_event_list = Event.objects.filter(start_date__gte=datetime.now()).order_by('start_date')
        venue = AbstractProfile.objects.select_subclasses().get(name='the wulf.')
             
        html_content = render_to_string('event_email.html', {'venue': venue, 'upcoming_event_list': upcoming_event_list})
        
        #print html_content
        
        text_part = strip_tags(html_content)
        
        # Image processing, replace the current image urls with attached images.
        soup = BeautifulSoup(html_content)
        
        #print soup
        #images = []
        #added_images = []
        for iframe in soup("iframe"):
                soup.iframe.extract()
    
        for index, tag in enumerate(soup.findAll('img' or 'header')):
            if tag.name == u'img':
                name = 'src'
            #elif tag.name == u'table':
            #    name = 'background'
            # If the image was already added, skip it.
            prefix = ''
            if tag[name][:4] != 'http':
                prefix =  'http://www.thewulf.org'
            tag[name] = prefix + tag[name]
            # If the image was already added, skip it.
#            If we want to attach the images
#             if tag[name] in added_images:
#                 continue
#             added_images.append(tag[name])
#             images.append((tag[name], 'img%d' % index))
#             tag[name] = 'cid:img%d' % index   
        html_content = str(soup)
        
        #print html_content

        
        #subject = '@ the wulf.: this sun. - 8 pm :: new works by Todd Lerew & Ingrid Lee'
        subject = args[0]
        
        msg = EmailMultiAlternatives(subject, text_part, 'info@thewulf.org',['info@thewulf.org'])
        #msg = EmailMultiAlternatives(subject, text_part, 'info@thewulf.org',['info@thewulf.org'])
        
            
#         for filename, file_id in images:
#             print filename
#             image_file = cStringIO.StringIO(urllib.urlopen(filename).read())
#             msg_image = MIMEImage(image_file.read())
#             image_file.close()
#             msg_image.add_header('Content-ID', '<%s>' % file_id)
#            msg.attach(msg_image)
            
        msg.attach_alternative(html_content, "text/html")
        
        msg.send()
