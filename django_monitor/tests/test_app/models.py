from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

import django_monitor

class Author(models.Model):
    """ Moderated model """
    name = models.CharField(max_length = 100)
    age = models.IntegerField()
    # To make sure that post_moderation signal is emitted.
    signal_emitted = models.BooleanField(editable = False, default = False)

    def __unicode__(self):
        return self.name

    def collect_signal(self):
        """Registers the emission of post_moderation signals"""
        self.signal_emitted = True
        self.save()

django_monitor.nq(Author)

def auth_moderation_handler(sender, instance, **kwargs):
    """
    Receives the post_moderation signal from Author & passes it to the instance
    """
    instance.collect_signal()

django_monitor.post_moderation.connect(
    auth_moderation_handler, sender = Author
)

class Publisher(models.Model):
    """ Not moderated model """
    name = models.CharField(max_length = 255)
    num_awards = models.IntegerField()

    def __unicode__(self):
        return self.name

class WebPub(Publisher):
    """ To check something with subclassed models """
    pass

class Book(models.Model):
    """ Moderated model with related objects """
    isbn = models.CharField(max_length = 9)
    name = models.CharField(max_length = 255)
    pages = models.IntegerField()
    authors = models.ManyToManyField(Author)
    publisher = models.ForeignKey(Publisher)
    
    def __unicode__(self):
        return self.name

django_monitor.nq(Book, ['supplements', ])

class EBook(Book):
    """ Subclassing a moderated model """
    pass

django_monitor.nq(EBook, ['supplements', ])

class Supplement(models.Model):
    """ Objects of this model get moderated along with Book"""
    serial_num = models.IntegerField()
    book = models.ForeignKey(Book, related_name = 'supplements')

    def __unicode__(self):
        return 'Supplement %s to %s' % (self.serial_num, self.book)

django_monitor.nq(Supplement)

class Reader(models.Model):
    """ To test an issue with custom querysets. See admin & tests """
    name = models.CharField(max_length = 100)
    user = models.ForeignKey(User)

django_monitor.nq(Reader)

