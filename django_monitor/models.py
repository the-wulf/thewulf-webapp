from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import datetime


from django.conf import settings
from django.core import serializers
from django.db.models.query import QuerySet

class SerializedObjectField(models.TextField):
    '''Model field that stores serialized value of model class instance
       and returns deserialized model instance
       
       >>> from django.db import models
       >>> import SerializedObjectField
       
       >>> class A(models.Model):
               object = SerializedObjectField(serialize_format='json')
               
       >>> class B(models.Model):
               field = models.CharField(max_length=10)
       >>> b = B(field='test')
       >>> b.save()
       >>> a = A()
       >>> a.object = b
       >>> a.save()
       >>> a = A.object.get(pk=1)
       >>> a.object
       <B: B object>
       >>> a.object.__dict__
       {'field': 'test', 'id': 1}
       
    '''
    def __init__(self, serialize_format='json', *args, **kwargs):
        self.serialize_format = serialize_format
        super(SerializedObjectField, self).__init__(*args, **kwargs)
        
    def _serialize(self, value):
        if not value:
            return ''
        
        if not isinstance(value, QuerySet):
            value = [value]
            
        return serializers.serialize(self.serialize_format, value, indent=4)
 
    def _deserialize(self, value):
        objs = [obj for obj in serializers.deserialize(self.serialize_format,
                                value.encode(settings.DEFAULT_CHARSET))]
        
        if len(objs) == 1:
            return objs[0].object
        else:
            return [obj.object for obj in objs]
 
    def db_type(self):
        return 'text'
 
    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname, None)
        return self._serialize(value)
 
    def contribute_to_class(self, cls, name):
        self.class_name = cls
        super(SerializedObjectField, self).contribute_to_class(cls, name)
        models.signals.post_init.connect(self.post_init)
 
    def post_init(self, **kwargs):
        if 'sender' in kwargs and 'instance' in kwargs:
            if kwargs['sender'] == self.class_name and \
            hasattr(kwargs['instance'], self.attname):
                value = self.value_from_object(kwargs['instance'])
                
                if value:
                    setattr(kwargs['instance'], self.attname,
                            self._deserialize(value))
                else:
                    setattr(kwargs['instance'], self.attname, None)

from django_monitor.conf import (
    STATUS_DICT, PENDING_STATUS, APPROVED_STATUS, CHALLENGED_STATUS
)
STATUS_CHOICES = STATUS_DICT.items()

class MonitorEntryManager(models.Manager):
    """ Custom Manager for MonitorEntry"""

    def get_for_instance(self, obj):
        ct = ContentType.objects.get_for_model(obj.__class__)
        try:
            mo = MonitorEntry.objects.get(content_type = ct, object_id = obj.pk)
            return mo
        except MonitorEntry.DoesNotExist:
            pass

class MonitorEntry(models.Model):
    """ Each Entry will monitor the status of one moderated model object"""
    objects = MonitorEntryManager()
    
    timestamp = models.DateTimeField(
        auto_now_add = True, blank = True, null = True
    )
    status = models.CharField(max_length = 2, choices = STATUS_CHOICES)
    status_by = models.ForeignKey(User, blank = True, null = True)
    status_date = models.DateTimeField(blank = True, null = True)
    notes = models.CharField(max_length = 100, blank = True)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    serialized_object = SerializedObjectField(serialize_format='json')

    class Meta:
        app_label = 'django_monitor'
        verbose_name = 'moderation Queue'
        verbose_name_plural = 'moderation Queue'

    def __unicode__(self):
        return "[%s] %s" % (self.get_status_display(), self.content_object)

    def get_absolute_url(self):
        if hasattr(self.content_object, "get_absolute_url"):
            return self.content_object.get_absolute_url()

    def _moderate(self, status, user, notes = ''):
        from django_monitor import post_moderation
        self.status = status
        self.status_by = user
        self.status_date = datetime.datetime.now()
        self.notes = notes
        self.save()
        # post_moderation signal will be generated now with the associated
        # object as the ``instance`` and its model as the ``sender``.
        sender_model = self.content_type.model_class()
        instance = self.content_object
        post_moderation.send(sender = sender_model, instance = instance)

    def approve(self, user = None, notes = ''):
        """Deprecated. Approve the object"""
        self._moderate(APPROVED_STATUS, user, notes)

    def challenge(self, user = None, notes = ''):
        """Deprectaed. Challenge the object """
        self._moderate(CHALLENGED_STATUS, user, notes)

    def reset_to_pending(self, user = None, notes = ''):
        """Deprecated. Reset status from Challenged to pending"""
        self._moderate(PENDING_STATUS, user, notes)

    def moderate(self, status, user = None, notes = ''):
        """
        Why a separate public method?
        To use when you're not sure about the status given
        """
        if status in STATUS_DICT.keys():
            self._moderate(status, user, notes)

    def is_approved(self):
        """ Deprecated"""
        return self.status == APPROVED_STATUS

    def is_pending(self):
        """ Deprecated."""
        return self.status == PENDING_STATUS

    def is_challenged(self):
        """ Deprecated."""
        return self.status == CHALLENGED_STATUS

MONITOR_TABLE = MonitorEntry._meta.db_table


