from django import template
from django.template import Context, Template
from thewulf.thewulfcms.models import *
from datetime import *
from thewulf import views
#from thewulf.views import work
import datetime
from django.core.files.storage import default_storage

register = template.Library()

#@register.inclusion_tag('event.html')
#def events_test():
#    upcoming_event_list = Event.objects.filter(start_date=datetime.now())
#    past_event_list = Event.objects.filter(start_date=datetime.now())
#    return {'upcoming_event_list': upcoming_event_list, 'past_event_list':past_event_list}

@register.filter('check_type')
def check_type(ob):
    return ob.__class__.__name__

from django_monitor.models import MonitorEntry
from django.contrib.contenttypes.models import ContentType

def pub(ob):
    content_type = ContentType.objects.get(app_label="thewulfcms", model=check_type(ob)).id
    mE = MonitorEntry.objects.get(content_type = content_type, object_id=ob.id)
#    e = Event.objects.get(name='test 2')
#    mE.serialized_object = e
#    mE.save()
#    p = Program.objects.get(id=1898)
#    mE.serialized_object = p
#    mE.save()
    test = mE.serialized_object
    return test

#class ModuleRenderer(template.Node):
#    def __init__(self, format_string):
#        self.format_string = format_string
#    def render(self, context):
##        return work('self.format_string', 'rts')  
##        you can also just return the template here
#        print(self.format_string)
#        t = template.loader.get_template('work_module.html')
#        return t.render(Context({'var':''}, autoescape=context.autoescape))

@register.inclusion_tag('profile_module.html')
def embed_profile_module(profile, verbose):
    return {'profile': profile, 'profile_type': check_type(profile), 'verbose': verbose }

@register.inclusion_tag('program_module.html')
def embed_program_module(eventpub):
    resultProgram = []
    previousWork = None
    currentWorkMovements = []
    
    event = Event.objects.get(pk=eventpub.pk)
    
    for program in event.program_set.all():
        for work in program.works.all().select_subclasses():
            
            if isinstance(work, Movement):
                print('movement is detected')
                if work.parent_work == previousWork:
                    # add to the previous work's array of movements
                    currentWorkMovements.append(work) 
                else:
                    
                    # create new array for the movements
                    currentWorkMovements = []
                    
                    currentWorkMovements.append(work)
                    previousWork = work.parent_work
                    resultProgram.append({ 'work': previousWork, 'movements': currentWorkMovements })
            else:
                print('work is detected')
                
                currentWorkMovements = []

                if len( work.movement_set.all() ) > 0:
                    for movement in work.movement_set.all():
                        currentWorkMovements.append(movement)
                previousWork = work
                resultProgram.append({ 'work': previousWork, 'movements': currentWorkMovements })
                
#    resultProgram.append({ 'work': previousWork, 'movements': currentWorkMovements })
    
    resultPerformers = event.performer_set.all().order_by('performer__name')
    
    return {'programs': resultProgram, 'performers':  resultPerformers }

@register.inclusion_tag('work_module.html')
def embed_work_module(arg, arg2):
    #Math goes here
    return {'blah': arg2}

@register.inclusion_tag('event_module.html')
def embed_event_module(event, verbose):
#    if event.is_approved() == True:
#        eventpub = event
#    else:
#        eventpub = pub(event)
    return {'verbose': verbose, 'event': event}

@register.filter(name='file_exists')
def file_exists(filepath):
    return default_storage.exists(filepath)


#@register.tag
#def embed(parser, token):
#    try:
#        # split_contents() knows not to split quoted strings.
#        tag_name, format_string = token.split_contents()
#
#    except ValueError:
#        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
#    if not (format_string[0] == format_string[-1] and format_string[0] in ('"', "'")):
#        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
#    return ModuleRenderer(format_string[1:-1])
#    