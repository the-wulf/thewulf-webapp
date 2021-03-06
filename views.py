from datetime import datetime, date
import itertools as it

from django.template import Context, loader, Library
from django.http import HttpResponse
from django.shortcuts import render_to_response

from thewulfcms.models import *
from django.template.loader import render_to_string

def home(request, name):
    fundraiser = Event.objects.get(name='the wulf. 2015 fundraiser')
    upcoming_event_list = Event.objects.filter(start_date__gte=datetime.now()).order_by('start_date')
    venue = AbstractProfile.objects.select_subclasses().get(name='the wulf.')
    return render_to_response('home.html', {'name': name, 'venue': venue, 'upcoming_event_list': upcoming_event_list, 'fundraiser': fundraiser})

def events(request, name):
    return events_by_year(request, name, date.today().year)

def events_by_year(request, name, year):
    fundraiser = Event.objects.get(name='the wulf. 2015 fundraiser')
    upcoming_event_list = Event.objects.filter(start_date__gte=datetime.now()).order_by('start_date')
    past_event_list = Event.objects.filter(start_date__year=year, start_date__lt=datetime.now()).order_by('-start_date')
    #past_event_list = Event.objects.filter(name = 'Experimental Music Yearbook')
    return render_to_response('events.html', {'name': name, 'upcoming_event_list':upcoming_event_list, 'past_event_list':past_event_list, 'fundraiser': fundraiser})
    
def event_details(request, name,  id):
    event = Event.objects.get(id = id)
    return render_to_response('event_details.html', {'event': event, 'verbose': 'true'})

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


def about(request, *args, **kwargs):
    return render_to_response('about.html', {})


def archive_list(request, year=None, month=None):
    queryset = Program.objects.select_related('event').order_by('event__start_date')
    qinfo = 'all'

    if year:
        queryset = queryset.filter(event__start_date__year=int(year))
        qinfo = year
    if month:
        queryset = queryset.filter(event__start_date__month=int(month))
        qinfo += ' %s' % month

    queryset = queryset.values('id', 'event__name', 'event__start_date')

    programs = OrderedDict()
    for item in queryset:
        group_date = item['event__start_date'].strftime('%Y %b'), item['event__start_date'].replace(day=1)
        programs.setdefault(group_date, [])
        item['display_date'] = item['event__start_date'].strftime('%Y %b %d')
        programs[group_date].append(item)

    return render_to_response('archive-list.html', {'programs': programs, 'qinfo': qinfo})


def archive_program_detail(request, program_id):

    program = get_object_or_404(Program, pk=program_id)
    works_performed = program.works.all()

    work_items = []
    for work in works_performed:
        audio = EventAudioRecording.objects.filter(works__id=work.pk, event__id=program.event.pk).first()
        video = EventVideo.objects.filter(works__id=work.pk, event__id=program.event.pk).first()
        work_items.append({
            'name': work.name,
            'authors': ','.join(it.chain(*work.authors.values_list('name')))
            'audio': audio,
            'video': video
        })

    return render_to_response('archive-program-detail.html', {'event': program.event, 'works': work_items})
