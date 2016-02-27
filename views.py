from django.template import Context, loader, Library
from django.http import HttpResponse
from django.shortcuts import render_to_response
from thewulfcms.models import *
from datetime import *
from django.template.loader import render_to_string

def home(request, name):
    fundraiser = Event.objects.get(name='the wulf. 2015 fundraiser')
    upcoming_event_list = Event.objects.filter(start_date__gte=datetime.now()).order_by('start_date')
    venue = AbstractProfile.objects.select_subclasses().get(name='the wulf.')
    return render_to_response('home.html', {'name': name, 'venue': venue, 'upcoming_event_list': upcoming_event_list, 'fundraiser': fundraiser})

def events(request, name):
    return events_by_year(request, name, '2016')

def events_by_year(request, name, year):
    fundraiser = Event.objects.get(name='the wulf. 2015 fundraiser')
    upcoming_event_list = Event.objects.filter(start_date__gte=datetime.now()).order_by('start_date')
    past_event_list = Event.objects.filter(start_date__year=year, start_date__lt=datetime.now()).order_by('-start_date')
    #past_event_list = Event.objects.filter(name = 'Experimental Music Yearbook')
    return render_to_response('events.html', {'name': name, 'upcoming_event_list':upcoming_event_list, 'past_event_list':past_event_list, 'fundraiser': fundraiser})
    
def event_detail(request, name,  id):
    event = Event.objects.get(id = id)
    return render_to_response('event_module.html', {'event': event, 'verbose': True})

def donate(request, name):
    fundraiser_event = Event.objects.get(name = 'the wulf. 2015 fundraiser')
    return render_to_response('donate.html', {'name': name, 'fundraiser_event': fundraiser_event})

def membership(request, name):
    fundraiser_event = Event.objects.get(name = 'the wulf. 2015 fundraiser')
    return render_to_response('membership.html', {'name': name, 'fundraiser_event': fundraiser_event})

def media(request, name):
    return render_to_response('media.html', {'name': name,})

def links(request, name):
    return render_to_response('links.html', {'name': name,})

def contact(request, name):
    return render_to_response('contact.html', {'name': name,})

def profiles(request, name):
    profiles = SingleProfile.objects.all()
    return render_to_response('profiles.html', {'name': name, 'profiles': profiles })

def profile(request, name, val):
    profiles = SingleProfile.objects.filter(pk=val)
    return render_to_response('profiles.html', {'name': name, 'profiles': profiles })


#def work(request, name):
#    if name == 'rtr':
#        return render_to_response('work.html', {})
#    else:
#        return render_to_string('work.html', {})
