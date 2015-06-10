from django.core.management.base import BaseCommand, CommandError
from django.template import Context, loader, Library
from thewulf.thewulfcms.models import *
import os
import re
from django.contrib.auth.models import User, Group
from datetime import *
from optparse import make_option

class Command(BaseCommand):
    
    help = "scrape the cards"
    
    def handle(self, *args, **options):
        card_scrape_db(args[0], args[1])



# <codecell>

def card_scrape_db(top_folder, date_string): 
    #initializing a few variables as empty strings
    piece = ''
    concert = ''
    basic_permissions_group = Group.objects.all()[0]
    
    for root,dirs,files in os.walk(top_folder): #walk through the specified directory
        for form in files:
            if form.endswith(date_string + ".txt"): #find all .txt files
                print(form)
                
                curatorProfileName = root.split('/')[-1]
                
                data = open(os.path.join(root, form))
                line = data.readline() #for line in data
                #initializing variables used later as empty strings
                eventName = ''
                pieceModel = ''
                programNote = ''
                performer = ''
                ins = ''
                #date_string = form.split('.')[0]
                track_count = 0
                position = 0
                while line:
                    #get concert title
                    if 'Concert_Title:' in line:
                        concertTitle = re.search('Concert_Title: (.*)',line)
                        concertTitle = concertTitle.group(1)
                        #finds event within database, else returns EVENT NOT FOUND
                        eventName = Event.objects.filter(name = concertTitle)
                        if len(eventName) == 0:
                            print 'EVENT NOT FOUND'
                        else:
                            eventName = eventName[0]
                        print concertTitle
                        Program.objects.filter(event = eventName).delete()
                        EventAudioRecording.objects.filter(event = eventName).delete()
                        EventVideo.objects.filter(event = eventName).delete()
                        Performer.objects.filter(event = eventName).delete()
                        
                    #get concert date
                    elif 'Concert_Date:' in line:
                        eventDate = re.search('Concert_Date: (.*)',line)
                        eventDate = eventDate.group(1)
                        print eventDate
                    
                    #get piece titles
                    #TODO: substitute "unknown" for unknown piece
                    elif 'Title:' in line:
                        piece = re.search('Title: (.*)',line)
                        piece = piece.group(1).lstrip()
                    
                    #get composer of pieces
                    elif 'Composer:' in line:
                        
                        pieceComposerList = []
                        composers = re.search('Composer: (.*)',line)
                        composers = composers.group(1).strip()
                        
                        composers = composers.replace('[', '').replace(']', '')
                        composers = composers.split(',')
                        u = ''
                        
                        for c in composers:
                            composer = ''
                            if c == 'NAMEXXX':
                                firstName = 'Composer'
                                lastName = 'Unknown'
                                composer = firstName + ' ' + lastName
                            else:
                                firstName = c.strip().split(' ')[0].strip()
                                lastName = c.strip().split(' ')[-1].strip()
                                composer = firstName + ' ' + lastName
                                composer = composer.title()
                        
                                #create a user for composer if one doesnt exist
                                u = User.objects.filter(first_name__exact=firstName, last_name__exact=lastName)
                                if len(u) == 0:
                                    u = User(first_name=firstName, last_name=lastName, username = (firstName[0] + lastName).lower(), is_staff = True)
                                    u.save()
                                    u.groups.add(basic_permissions_group)
                                    u.save()
                                else:
                                    u = u[0]
                            
                            #create single profile for composer if one doesnt exist  
                            pieceComposer = SingleProfile.objects.filter(name__exact=composer)
                            if len(pieceComposer) == 0:
                                pieceComposer = SingleProfile(name = composer, is_author = True)
                                pieceComposer.save()
                            else:
                                pieceComposer = pieceComposer[0]
                                print 'composer exists in database!'
                            if u != '':
                                pieceComposer.users.add(u)
                            pieceComposerList.append(pieceComposer)
                            
                        #create a work by specific composer if pieces doesnt exist
                        if piece == 'TITLEXXX':
                            piece = 'Piece Unknown :: ' + composer
                        pieceModel = Work.objects.filter(name__exact=piece)
                        if len(pieceModel) == 0:
                            pieceModel = Work(name = piece)
                            pieceModel.save()
                        else:
                            pieceModel = pieceModel[0]
                            print 'work exists in database!'
                            
                        
                        authors = pieceModel.authors.all()
                        
                        for pieceComposer in pieceComposerList:
                            if pieceComposer not in authors:
                                pieceModel.authors.add(pieceComposer)
                                pieceModel.save()
                        
                        track_count += 1
                        prefix = '0'
                        if track_count > 9:
                            prefix = ''
                            
                        #eventRecording = EventAudioRecording.objects.filter(event = eventName, works = pieceModel)
                        #if len(eventRecording) == 0:
                        #    rec = EventAudioRecording(event = eventName, position = position)
                        #    rec.save()
                        #else:
                        #    rec = eventRecording[0]
                        #    print 'event recording exists!'
                        
                        rec = EventAudioRecording(event = eventName, position = position)
                        rec.save()
                        
                        vid = EventVideo(event = eventName, position = position)
                        vid.save()
                                
                        piecesList = rec.works.all()
                        
                        if pieceModel not in piecesList:
                            rec.works.add(pieceModel)
                            rec.save()
                            rec.uncompressed_master_recording.name = 'events/' + date_string + '/uncompressed_mastered_recordings/' + prefix + str(track_count) + ".wav"
                            rec.compressed_master_recording.name = 'events/' + date_string + '/compressed_mastered_recordings/' + prefix + str(track_count) + ".ogg"
                            rec.save()
                            
                            vid.works.add(pieceModel)
                            vid.save()
                            vid.media_file.name = 'events/' + date_string + '/videos/' + prefix + str(track_count) + ".mov"
                            vid.save()
                        
                    #get name, email and instrument of each performer       
                    elif 'Performers:' in line and '//Performers' not in line:
                        performers = re.search('Performers: (.*)',line)
                        performers = performers.group(1).strip()
                        performers = performers.split(';')
                        performers = performers[:-1]
                        performers = [p for p in performers if p.strip() != 'NAME, EMAIL, INS']
                        performerEmail = ''
                        u = ''
                        
                        for p in performers:
                            e = p.split(',')
                            performer = e[0].strip()
                            if performer == 'NAME':
                                firstName = 'Performer'
                                lastName = 'Unknown'
                                performer = firstName + ' ' + lastName
                            else:
                                firstName = performer.split(' ')[0].strip()
                                lastName = performer.split(' ')[-1].strip()
                                performer = firstName + ' ' + lastName
                                performer = performer.title()
                            
                                
                                
                                #check to see if a user for performer exists, creates a user if one doesnt exist
                                u = User.objects.filter(first_name__exact=firstName, last_name__exact=lastName)
                                if len(u) == 0:
                                    u = User(first_name=firstName, last_name=lastName, username = (firstName[0] + lastName).lower(), is_staff = True)
                                    u.save()
                                    u.groups.add(basic_permissions_group)
                                    u.save()
                                else: 
                                    u = u[0]
                                
                                #checks if email exists in database. if it doesnt, adds email to created user profile    
                                performerEmail = e[1].strip()
                                if performerEmail != 'EMAIL':
                                    u.email = performerEmail
                                    u.save()
#                                 else:
#                                     performerEmail = performerEmail[0]
                            
                            #checks if an instrument exists, and creates one if it doesnt
                            if len(e) > 3:
                                instruments = ''
                                for ins_String in e[2:]:
                                    instruments = instruments + ins_String + ','
                                instruments = instruments[:-2]
                            else:
                                instruments = e[2]
                            insForLater = []
                            if instruments.strip() != 'INS':
                                instruments = instruments.replace('[', '').replace(']', '')
                                
                                instruments = instruments.split(',')
                                
                                for instrument in instruments:
                                    ins = Instrument.objects.filter(name__exact = instrument.strip())
                                    if len(ins) == 0:
                                        ins = Instrument(name = instrument.strip())
                                        ins.save()
                                    else:
                                        ins = ins[0]
                                    insForLater.append(ins)
                            else:
                                ins = Instrument.objects.filter(name__exact = 'instrument unknown')
                                insForLater.append(ins[0])
                                    
                            
                            #checks if a single profile for performer exists, creates one if it doesnt
                            performerObject = SingleProfile.objects.filter(name__exact=performer)
                            
                            if len(performerObject) == 0:
                                performerObject = SingleProfile(name = performer, is_performer = True)
                                performerObject.save()
                            else:
                                performerObject = performerObject[0]
                            
                            #links email to created single profile
                            if performerEmail != 'EMAIL':
                                profileEmail = Email.objects.filter(email__exact = performerEmail.strip())
                                if len(profileEmail) == 0:
                                    profileEmail = Email(email = performerEmail.strip())
                                    profileEmail.save()
                                else:
                                    profileEmail = profileEmail[0]
                                performerObject.emails.add(profileEmail)
                                performerObject.save()
                            if u != '':  
                                performerObject.users.add(u)
                            
                            #inserts performers field per performer, connecting them to an event, a work, and an instrument
                            eventPerformer = Performer.objects.filter(event = eventName, performer = performerObject, instruments__in = insForLater)
                            if len(eventPerformer) == 0:
                                eventPerformer = Performer(event = eventName, performer = performerObject)
                                eventPerformer.save()
                                for ins in insForLater:
                                    eventPerformer.instruments.add(ins)
                                    eventPerformer.save()
                            else:
                                eventPerformer = eventPerformer[0]
                                if len(eventPerformer.instruments.all()) != len(insForLater):
                                    eventPerformer = Performer(event = eventName, performer = performerObject)
                                    eventPerformer.save()
                                    for ins in insForLater:
                                        eventPerformer.instruments.add(ins)
                                        eventPerformer.save()
                                print 'event performer exists!'
                            eventPerformer.works.add(pieceModel)
                            eventPerformer.save()
                            
                    
                    #gets start time of piece
                    elif 'Start_Time:' in line:
                        startTime = re.search('Start_Time: (.*)',line)
                        startTime = startTime.group(1)
                    
                    #gets end time of piece
                    elif 'End_Time:' in line:
                        endTime = re.search('End_Time: (.*)',line)
                        endTime = endTime.group(1)
                    
                    #a boolean if streaming is allowed
                    elif 'Allow_Streaming:' in line:
                        allowStreaming = re.search('Allow_Streaming: (.*)',line)
                        allowStreaming = allowStreaming.group(1)
                    
                    #a boolean if downloading is allowed
                    elif 'Allow_Download:' in line:
                        allowDownload = re.search('Allow_Download: (.*)',line)
                        allowDownload = allowDownload.group(1)
                    
                    #gets program notes for each piece by reading after 'Program_Note: ' until a double line break.
                    elif 'Program_Note:' in line:
                        programNote = re.search('Program_Note: (.*)',line)
                        programNote = programNote.group(1)
                        if programNote == 'TEXTXXX':
                            programNote = ''
                        else:
                            subline = data.readline()
                            while subline and subline.strip() != '':
                                programNote += subline
                                subline = data.readline()
                        
                        #creating a program for an existing event.
                        #eventProgram = Program.objects.filter(event=eventName, works = pieceModel)
                        #if len(eventProgram) == 0:
                        #    eventProgram = Program(event = eventName, program_note = programNote, position = position)
                        #    eventProgram.save()
                        #else:
                        #    eventProgram = eventProgram[0]
                        #    print 'event program exists!'
                        eventProgram = Program(event = eventName, program_note = programNote, position = position)
                        eventProgram.save()    
                        eventProgram.works.add(pieceModel)
                        eventProgram.save()
                        position += 1
                        
                    
                        
                    line = data.readline()
                    
                firstName = curatorProfileName.split(' ')[0].strip()
                lastName = curatorProfileName.split(' ')[-1].strip()
                curatorProfileName = firstName + ' ' + lastName
                curatorProfileName = curatorProfileName.title()
                curator = SingleProfile.objects.filter(name = curatorProfileName)
                eventName.curators.add(curator[0])
                u = User.objects.filter(first_name__exact=firstName, last_name__exact=lastName)
                eventName.users.add(u[0])
                eventName.save()
                