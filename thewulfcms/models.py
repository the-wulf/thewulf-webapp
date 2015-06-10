from django.db import models
from django.contrib.auth.models import User, Group
from model_utils.managers import InheritanceManager
import os.path
from datetime import datetime

from django.core.cache import cache


import django_monitor

class AbstractModel(models.Model):
    short_description = models.TextField(blank = True)
    description = models.TextField(blank = True)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_edited_date = models.DateTimeField(auto_now=True)
    users = models.ManyToManyField(User, blank=True)
    groups = models.ManyToManyField(Group, blank=True)  
    
    def delete(self, *args, **kwargs):
        cache.clear()
        super(AbstractModel, self).delete(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        cache.clear()
        super(AbstractModel, self).save(*args, **kwargs)
    
class Category(AbstractModel):
    name = models.CharField(max_length = 100)
    
    class Meta:
        verbose_name_plural = "categories"
    
    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)
    
    def related_label(self):
        return "%s" % (self.name)
    
    def __unicode__(self):
        return self.name
    
    
class Post(AbstractModel):
    name = models.CharField(max_length = 100)
    category = models.ManyToManyField(Category)
    
    def __unicode__(self):
        return self.name
    
    
class Instrument(AbstractModel):
    name = models.CharField(max_length = 100)
    
    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)
    
    def related_label(self):
        return "%s" % (self.name)
    
    def __unicode__(self):
        return self.name
    
    
class Email(models.Model):
    email = models.EmailField(blank=True)
    
    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "email__icontains",)

    def related_label(self):
        return "%s" % (self.email)
    
    def __unicode__(self):
        return self.email
    

class Weblink(models.Model):
    url = models.URLField(verify_exists=True, blank=True)
    
    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "url__icontains",)

    def related_label(self):
        return "%s" % (self.url)
    
    def __unicode__(self):
        return self.url
    

class AbstractProfile(models.Model):
    short_description = models.TextField(blank = True)
    description = models.TextField(blank = True)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_edited_date = models.DateTimeField(auto_now=True)
    users = models.ManyToManyField(User, blank=True)
    groups = models.ManyToManyField(Group, blank=True)  
    
    name = models.CharField(max_length = 100)
    address_1 = models.CharField(max_length = 100, blank=True)
    address_2 = models.CharField(max_length = 100, blank=True)
    city = models.CharField(max_length = 100, blank=True)
    state = models.CharField(max_length = 100, blank=True)
    country = models.CharField(max_length = 100, blank=True)
    zip_code = models.CharField(max_length = 20, blank=True)
    phone_number_1 = models.CharField(max_length = 20, blank=True)
    phone_number_2 = models.CharField(max_length = 20, blank=True)
    weblinks = models.ManyToManyField(Weblink, blank=True)
    emails = models.ManyToManyField(Email, blank=True)
    birth_date = models.DateField(blank=True, null = True)
    death_date = models.DateField(blank=True, null = True)
    mailing_list_optout = models.BooleanField(default=False, blank = False)
    is_member = models.BooleanField()
    
    objects = InheritanceManager()
    
    class Meta:
        verbose_name = "all profiles"
        verbose_name_plural = "all profiles"
    
    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)

    def related_label(self):
        return "%s" % (self.name)
    
    def __unicode__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        cache.clear()
        super(AbstractProfile, self).delete(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        cache.clear()
        super(AbstractProfile, self).save(*args, **kwargs)
    
    
class SingleProfile(AbstractProfile):
    is_performer = models.BooleanField()
    is_author = models.BooleanField()
    primary_instruments = models.ManyToManyField(Instrument, blank=True)
    
    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)

    def related_label(self):
        return "%s" % (self.name)
    
    def __unicode__(self):
        return self.name
    

class GroupProfile(AbstractProfile):   
    members = models.ManyToManyField(SingleProfile, blank=True)
    
    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)

    def related_label(self):
        return "%s" % (self.name)
    
    def __unicode__(self):
        return self.name
    
    
class VenueProfile(AbstractProfile):

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)
    
    def related_label(self):
        return "%s" % (self.name)
    
    def __unicode__(self):
        return self.name
    
    
class AbstractWork(models.Model):
    short_description = models.TextField(blank = True)
    description = models.TextField(blank = True)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_edited_date = models.DateTimeField(auto_now=True)
    users = models.ManyToManyField(User, blank=True)
    groups = models.ManyToManyField(Group, blank=True)
    
    name = models.CharField(max_length = 100)
    authors = models.ManyToManyField(AbstractProfile)
    creation_date_start = models.DateField(blank = True, null = True)
    creation_date_end = models.DateField(blank = True, null = True)
    score = models.FileField(upload_to='scores', blank = True)
    instrumentation = models.ManyToManyField(Instrument, blank = True)
    
    objects = InheritanceManager()
    
    class Meta:
        verbose_name = "works and movements"
        verbose_name_plural = "works and movements"
    
    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)
    
    def related_label(self):
        return "%s" % (self.name)
    
    def __unicode__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        cache.clear()
        super(AbstractWork, self).delete(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        cache.clear()
        super(AbstractWork, self).save(*args, **kwargs)

    
class Work(AbstractWork):
    is_multi_movement = models.BooleanField()
    
    def __unicode__(self):
        return self.name

class Movement(AbstractWork):
    parent_work = models.ForeignKey(Work)
    movement_number = models.PositiveSmallIntegerField(blank = True, null = True)
    position = models.PositiveSmallIntegerField(blank = True, null = True)
    
    def __unicode__(self):
        return "%s: %s" % (self.parent_work, self.name)
    
    class Meta:
        ordering = ['position']

def update_event_program_filename(instance, filename):
        path = "events/%s/programs/" % (datetime.strftime(instance.start_date,"%Y_%m_%d"))
        fname = filename
        return os.path.join(path, fname)
    
class AbstractEvent(models.Model):
    short_description = models.TextField(blank = True)
    description = models.TextField(blank = True)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_edited_date = models.DateTimeField(auto_now=True)
    users = models.ManyToManyField(User, blank=True)
    groups = models.ManyToManyField(Group, blank=True)
    
    name = models.CharField(max_length = 100)
    start_date = models.DateField()
    start_time = models.TimeField()
    end_date = models.DateField(blank = True, null = True)
    end_time = models.TimeField(blank = True, null = True)
    curators = models.ManyToManyField(AbstractProfile, blank = True)
    venues = models.ManyToManyField(VenueProfile, related_name="thewulfcms_venues_related")
    program_notes = models.FileField(upload_to=update_event_program_filename, blank = True)
    
    objects = InheritanceManager()
    
    def __unicode__(self):
        return "%s: %s" % (self.start_date, self.name)
    
    class Meta:
        verbose_name = 'all events'
        verbose_name_plural = 'all events'
        
    def delete(self, *args, **kwargs):
        cache.clear()
        super(AbstractEvent, self).delete(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        cache.clear()
        super(AbstractEvent, self).save(*args, **kwargs)
    
    
class Installation(AbstractEvent):
    
    def __unicode__(self):
        return "%s: %s" % (self.start_date, self.name)
    
def update_event_rawrecording_filename(instance, filename):
        path = "events/%s/raw_audio_recordings/" % (datetime.strftime(instance.start_date,"%Y_%m_%d"))
        fname = filename
        return os.path.join(path, fname)
    
    
class Event(AbstractEvent):
    # we need to rethink this for multitrack recordings - maybe a zip file?
    raw_audio_recording = models.FileField(upload_to=update_event_rawrecording_filename, blank = True)
    
    def __unicode__(self):
        return "%s: %s" % (self.start_date, self.name)
    
# this is like performances
class Program(models.Model):
    event = models.ForeignKey(AbstractEvent)
    works = models.ManyToManyField(AbstractWork)
    program_note = models.TextField(blank = True)
    position = models.PositiveSmallIntegerField(blank = True, null = True)
    class Meta:
        ordering = ['position']
        verbose_name = 'work'
        verbose_name_plural = 'program'
        
    def delete(self, *args, **kwargs):
        cache.clear()
        super(Program, self).delete(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        cache.clear()
        super(Program, self).save(*args, **kwargs)
    
class Performer(models.Model):
    event = models.ForeignKey(Event)
    performer = models.ForeignKey(SingleProfile)
    group = models.ForeignKey(GroupProfile, blank = True, null = True)
    instruments = models.ManyToManyField(Instrument)
    works = models.ManyToManyField(AbstractWork)
    position = models.PositiveSmallIntegerField(blank = True, null = True)
    class Meta:
        ordering = ['position']
        
    def delete(self, *args, **kwargs):
        cache.clear()
        super(Performer, self).delete(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        cache.clear()
        super(Performer, self).save(*args, **kwargs)
    
class Media(AbstractModel):
    credit = models.CharField(max_length = 100, blank = True)
    position = models.PositiveSmallIntegerField(blank = True, null = True)
    class Meta:
        ordering = ['position']    

def update_event_audiorecordingcompressed_filename(instance, filename):
        path = "events/%s/compressed_mastered_recordings/" % (datetime.strftime(instance.event.start_date,"%Y_%m_%d"))
        fname = filename
        return os.path.join(path, fname)

def update_event_audiorecordinguncompressed_filename(instance, filename):
        path = "events/%s/uncompressed_mastered_recordings/" % (datetime.strftime(instance.event.start_date,"%Y_%m_%d"))
        fname = filename
        return os.path.join(path, fname)
    
# you can tag works but perhaps you should be able to tag people too
class EventAudioRecording(Media):
    compressed_master_recording = models.FileField(upload_to=update_event_audiorecordingcompressed_filename, blank = True)
    uncompressed_master_recording = models.FileField(upload_to=update_event_audiorecordinguncompressed_filename, blank = True)
    event = models.ForeignKey(AbstractEvent)
    works = models.ManyToManyField(AbstractWork)
    is_streaming_disabled = models.BooleanField(default=False, blank = False)
    is_downloading_disabled = models.BooleanField(default=False, blank = False)
    
    def __unicode__(self):
        return "Event Audio Recording"
    
def update_event_video_filename(instance, filename):
        path = "events/%s/videos/" % (datetime.strftime(instance.event.start_date,"%Y_%m_%d"))
        fname = filename
        return os.path.join(path, fname)
    
class EventVideo(Media):
    media_file = models.FileField(upload_to=update_event_video_filename)
    event = models.ForeignKey(AbstractEvent)
    works = models.ManyToManyField(AbstractWork, blank = True)
    
    def __unicode__(self):
        return "Event Video"
    
# this is an example of how we change name for a file upload. 
# we need to think about the directory structure here a bit more
def update_event_pic_filename(instance, filename):
        path = "events/%s/pics" % (datetime.strftime(instance.event.start_date,"%Y_%m_%d"))
        fname = filename
        return os.path.join(path, fname)
    
class EventPic(Media):
    media_file = models.FileField(upload_to=update_event_pic_filename)
    event = models.ForeignKey(AbstractEvent)
    works = models.ManyToManyField(AbstractWork, blank = True)
    
    def __unicode__(self):
        return "Event Pic"
    
def update_profile_audiorecording_filename(instance, filename):
        path = "profiles/%s/audio_recordings" % (instance.profile.pk)
        fname = filename
        return os.path.join(path, fname)
    
class ProfileAudioRecording(Media):
    media_file = models.FileField(upload_to=update_profile_audiorecording_filename)
    profile = models.ForeignKey(AbstractProfile)
    works = models.ManyToManyField(AbstractWork, blank = True)
    
    def __unicode__(self):
        return "Profile Audio Recording"
    
def update_profile_video_filename(instance, filename):
        path = "profiles/%s/videos" % (instance.profile.pk)
        fname = filename
        return os.path.join(path, fname)
    
class ProfileVideo(Media):
    media_file = models.FileField(upload_to=update_profile_video_filename)
    profile = models.ForeignKey(AbstractProfile)
    works = models.ManyToManyField(AbstractWork, blank = True)
    
    def __unicode__(self):
        return "Profile Video"
    
def update_profile_pic_filename(instance, filename):
        path = "profiles/%s/pics" % (instance.profile.pk)
        fname = filename
        return os.path.join(path, fname)
    
class ProfilePic(Media):
    media_file = models.FileField(upload_to=update_profile_pic_filename)
    profile = models.ForeignKey(AbstractProfile)
    works = models.ManyToManyField(AbstractWork, blank = True)
    
    def __unicode__(self):
        return "Profile Pic"

def update_post_audiorecording_filename(instance, filename):
        path = "posts/%s/audio_recordings" % (instance.post.pk)
        fname = filename
        return os.path.join(path, fname)
    
class PostAudioRecording(Media):
    media_file = models.FileField(upload_to=update_post_audiorecording_filename)
    post = models.ForeignKey(Post)
    works = models.ManyToManyField(AbstractWork, blank = True)
    
    def __unicode__(self):
        return "Post Audio Recording"

def update_post_video_filename(instance, filename):
        path = "posts/%s/videos" % (instance.post.pk)
        fname = filename
        return os.path.join(path, fname)
    
class PostVideo(Media):
    media_file = models.FileField(upload_to=update_post_video_filename)
    post = models.ForeignKey(Post)
    works = models.ManyToManyField(AbstractWork, blank = True)
    
    def __unicode__(self):
        return "Post Video"
    
def update_post_pic_filename(instance, filename):
        path = "posts/%s/pics" % (instance.post.pk)
        fname = filename
        return os.path.join(path, fname)
    
class PostPic(Media):
    media_file = models.FileField(upload_to=update_post_pic_filename)
    post = models.ForeignKey(Post)
    works = models.ManyToManyField(AbstractWork, blank = True)
    
    def __unicode__(self):
        return "Post Pic"
    
django_monitor.nq(Category)
django_monitor.nq(Post, rel_fields = ['postaudiorecording_set', 'postvideo_set', 'postpic_set'])
django_monitor.nq(Instrument)
django_monitor.nq(Email)
django_monitor.nq(Weblink)
django_monitor.nq(AbstractProfile, rel_fields = ['profileaudiorecording_set', 'profilevideo_set', 'profilepic_set'])
django_monitor.nq(SingleProfile, rel_fields = ['profileaudiorecording_set', 'profilevideo_set', 'profilepic_set'])
django_monitor.nq(GroupProfile, rel_fields = ['profileaudiorecording_set', 'profilevideo_set', 'profilepic_set'])
django_monitor.nq(VenueProfile, rel_fields = ['profileaudiorecording_set', 'profilevideo_set', 'profilepic_set'])
django_monitor.nq(VenueProfile)
django_monitor.nq(AbstractWork)
django_monitor.nq(Work,rel_fields = ['movement_set'])
django_monitor.nq(Movement)
django_monitor.nq(AbstractEvent, rel_fields = ['program_set','performer_set', 'eventaudiorecording_set', 'eventvideo_set', 'eventpic_set'])
django_monitor.nq(Event, rel_fields = ['program_set','performer_set', 'eventaudiorecording_set', 'eventvideo_set', 'eventpic_set'])
django_monitor.nq(Installation, rel_fields = ['program_set', 'eventaudiorecording_set', 'eventvideo_set', 'eventpic_set'])
django_monitor.nq(Program)
django_monitor.nq(Performer)
django_monitor.nq(EventAudioRecording)
django_monitor.nq(EventPic)
django_monitor.nq(EventVideo)
django_monitor.nq(ProfileAudioRecording)
django_monitor.nq(ProfilePic)
django_monitor.nq(ProfileVideo)
django_monitor.nq(PostAudioRecording)
django_monitor.nq(PostPic)
django_monitor.nq(PostVideo)


