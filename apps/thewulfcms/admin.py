from models import *
from forms import *
from django.contrib import admin
from django.conf.urls.defaults import patterns
from django.conf import settings
import os.path

from django_monitor.admin import MonitorAdmin

from django_monitor.models import MonitorEntry
from django.contrib.contenttypes.models import ContentType

def splitpath(path, maxdepth=20):
    ( head, tail ) = os.path.split(path)
    return splitpath(head, maxdepth - 1) + [ tail ] if maxdepth and head and head != path else [ head or tail ]

def check_type(ob):
    return ob.__class__.__name__

class MediaInline(admin.StackedInline):
    
    class Media:
        js = (settings.STATIC_URL+'/grappelli/tinymce/jscripts/tiny_mce/tiny_mce_src.js',settings.STATIC_URL+'grappelli/tinymce_setup/tinymce_setup.js')
        
    raw_id_fields = ('works',)
    form = SortableInlineForm
    autocomplete_lookup_fields = {
        'm2m': ['works'],
    }
    extra = 0
    sortable_field_name = "position"
    fields = ('short_description','works' ,'media_file','position')
#    classes = ('collapse closed',)
#    inline_classes = ('collapse open',)
    
#    def save_model(self, request, obj, form, change):
#        obj.save()
#        if not change:
#            obj.users.add(request.user)
#        obj.save()
#
#    def queryset(self, request):
#        qs = super(MediaInline, self).queryset(request)
#        if request.user.is_superuser:
#            return qs
#        return qs.filter(users=request.user)

# overriding change form does not work here
#    def get_form(self, request, obj=None, **kwargs):
#        if request.user.is_superuser:
#            kwargs['fields'] = ('short_description','works' ,'media_file','users','groups','position')
#        else:
#            kwargs['fields'] = ('short_description','works' ,'media_file','position')
#        return super(MediaInline, self).get_form(request, obj, **kwargs)
     
class EventMediaInline(MediaInline):
    fk_name = 'event'
    
class EventAudioInline(EventMediaInline):
    model = EventAudioRecording
    fields = ('short_description','works' ,'uncompressed_master_recording','compressed_master_recording','is_streaming_disabled','is_downloading_disabled', 'position')
     
class EventPicInline(EventMediaInline):
    model = EventPic
    
class EventVideoInline(EventMediaInline):
    model = EventVideo
    
class ProfileMediaInline(MediaInline):
    fk_name = 'profile'
    
class ProfileAudioInline(ProfileMediaInline):
    model = ProfileAudioRecording
    
class ProfilePicInline(ProfileMediaInline):
    model = ProfilePic
    
class ProfileVideoInline(ProfileMediaInline):
    model = ProfileVideo
    
class PostMediaInline(MediaInline):
    fk_name = 'post'
    
class PostAudioInline(PostMediaInline):
    model = PostAudioRecording
    
class PostPicInline(PostMediaInline):
    model = PostPic
    
class PostVideoInline(PostMediaInline):
    model = PostVideo
    
class MovementsInline(admin.StackedInline):
    
    class Media:
        js = (settings.STATIC_URL+'/grappelli/tinymce/jscripts/tiny_mce/tiny_mce_src.js',settings.STATIC_URL+'grappelli/tinymce_setup/tinymce_setup.js')
        
    fk_name = 'parent_work'
    model = Movement
    extra = 0
    form = SortableInlineForm
    raw_id_fields = ('authors','instrumentation',)  
    autocomplete_lookup_fields = {
        'm2m': ['authors','instrumentation'],
    }
    sortable_field_name = "position"
    # need to decide about whether to add descriptions at this level
    fields = ('name','parent_work','movement_number','authors','instrumentation',
              'creation_date_start','creation_date_end','score','position')
    
    def save_model(self, request, obj, form, change):
        obj.save()
        if not change:
            obj.users.add(request.user)
        obj.save()
        
    def queryset(self, request):
        qs = super(MovementsInline, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(users=request.user)

# overriding change form does not work here
#    def get_form(self, request, obj=None, **kwargs):
#        if request.user.is_superuser:
#            # need to decide about whether to add descriptions at this level
#            kwargs['fields'] = ('name','parent_work','movement_number','authors','instrumentation',
#              'creation_date_start','creation_date_end','score','users','groups','position')
#        else:
#            kwargs['fields'] = ('name','parent_work','movement_number','authors','instrumentation',
#              'creation_date_start','creation_date_end','score','position')
#        return super(MovementsInline, self).get_form(request, obj, **kwargs)

class AbstractWorkAdmin(MonitorAdmin):
    
    class Media:
        js = (settings.STATIC_URL+'/grappelli/tinymce/jscripts/tiny_mce/tiny_mce_src.js',settings.STATIC_URL+'grappelli/tinymce_setup/tinymce_setup.js')
        
    raw_id_fields = ('authors','instrumentation',)
    autocomplete_lookup_fields = {
        'm2m': ['authors','instrumentation'],
    }
    
    ordering = ['name']
    
    def save_model(self, request, obj, form, change):
        obj.save()
        if not change:
            obj.users.add(request.user)
        obj.save()
        
#    def save_model(self, request, obj, form, change):
#        if not request.user.is_superuser:
#            content_type = ContentType.objects.get(app_label="thewulfcms", model=check_type(obj)).id
#            mE = MonitorEntry.objects.get(content_type = content_type, object_id=obj.id)
#            e = Event.objects.get(pk = obj.pk)
#            mE.serialized_object = e
#            mE.save()
#            obj.reset_to_pending(user = request.user, notes = '')
#        obj.save()
    
    def queryset(self, request):
        qs = super(AbstractWorkAdmin, self).queryset(request)
#        this is how I should be checking paths all over
        testlist = ['event', 'abstractevent', 'installation']
        if request.user.is_superuser or splitpath(request.META['HTTP_REFERER'])[-3] in testlist:
            return qs.select_subclasses()
        return qs.select_subclasses().filter(users=request.user)
    
    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            # add description or not
            kwargs['fields'] = ('name','movement_number','authors','instrumentation',
              'creation_date_start','creation_date_end','score','users', 'groups',)
        else:
            kwargs['fields'] = ('name','movement_number','authors','instrumentation',
              'creation_date_start','creation_date_end','score')
        
        if request.path == '/admin/thewulfcms/abstractwork/addwork/':
            obj = Work()
        elif request.path == '/admin/thewulfcms/abstractwork/addmovement/':
            obj = Movement()
        return admin.site._registry[type(obj)].get_form(request, obj, **kwargs)
    
    
    def add_view(self, request, form_url='', extra_context=None):
        if not extra_context:
            extra_context = {}
        
        extra_context['is_abstract'] = True
        if request.path == '/admin/thewulfcms/abstractwork/addwork/':
            extra_context['type'] = 'work'
# This seems to work. hack?
            self.inlines=[MovementsInline,]
            self.inline_instances=[]
            for inline_class in self.inlines:
                inline_instance = inline_class(Work, self.admin_site)
                self.inline_instances.append(inline_instance)
        elif request.path == '/admin/thewulfcms/abstractwork/addmovement/':
            extra_context['type'] = 'movement'
            self.inlines=[]
            self.inline_instances=[]
            for inline_class in self.inlines:
                inline_instance = inline_class(Movement, self.admin_site)
                self.inline_instances.append(inline_instance)
        return super(AbstractWorkAdmin, self).add_view(request, form_url, extra_context)
    
    def change_view(self, request, object_id, extra_context=None):
        if not extra_context:
            extra_context = {}
            
        obj=AbstractWork.objects.filter(id=object_id).select_subclasses()
        
        extra_context['is_abstract'] = True
        if check_type(obj[0]) == 'Work':
            extra_context['type'] = 'work'
            self.inlines=[MovementsInline,]
            self.inline_instances=[]
            for inline_class in self.inlines:
                inline_instance = inline_class(Work, self.admin_site)
                self.inline_instances.append(inline_instance)
        elif check_type(obj[0]) == 'Movement':
            extra_context['type'] = 'movement'
            self.inlines=[]
            self.inline_instances=[]
            for inline_class in self.inlines:
                inline_instance = inline_class(Movement, self.admin_site)
                self.inline_instances.append(inline_instance)
        return super(AbstractWorkAdmin, self).change_view(request, object_id, extra_context)

    def changelist_view(self, request, extra_context=None):
        if not extra_context:
            extra_context = {}
        
        extra_context['is_abstract'] = True
        extra_context['children'] = ['work','movement',]
        return super(AbstractWorkAdmin, self).changelist_view(request, extra_context)
    
    def get_urls(self):
        urls = super(AbstractWorkAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^addwork/$', self.admin_site.admin_view(self.add_view)),
            (r'^addmovement/$', self.admin_site.admin_view(self.add_view))
        )
        return my_urls + urls
    
class WorkAdmin(MonitorAdmin):
    
    class Media:
        js = (settings.STATIC_URL+'/grappelli/tinymce/jscripts/tiny_mce/tiny_mce_src.js',settings.STATIC_URL+'grappelli/tinymce_setup/tinymce_setup.js')
        
    raw_id_fields = ('authors','instrumentation',)
    autocomplete_lookup_fields = {
        'm2m': ['authors','instrumentation'],
    }
    inlines = [MovementsInline]
    
    ordering = ['name']
    
    readonly_fields = ()
    
    def save_model(self, request, obj, form, change):
        obj.save()
        if not change:
            obj.users.add(request.user)
        obj.save()

    def queryset(self, request):
        qs = super(WorkAdmin, self).queryset(request)
        if request.user.is_superuser or splitpath(request.META['HTTP_REFERER'])[-3]=='event':
            return qs
        return qs.filter(users=request.user)
    
    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            kwargs['fields'] = ('name','authors','instrumentation',
              'creation_date_start','creation_date_end','score','users','groups')
        else:
            kwargs['fields'] = ('name','authors','instrumentation',
              'creation_date_start','creation_date_end','score')
        return super(WorkAdmin, self).get_form(request, obj, **kwargs)
    
    
class MovementAdmin(MonitorAdmin):
    
    class Media:
        js = (settings.STATIC_URL+'/grappelli/tinymce/jscripts/tiny_mce/tiny_mce_src.js',settings.STATIC_URL+'grappelli/tinymce_setup/tinymce_setup.js')
        
    raw_id_fields = ('authors','instrumentation',)
    autocomplete_lookup_fields = {
        'm2m': ['authors','instrumentation'],
    }
    
    ordering = ['name']
    
    readonly_fields = ()
    
    def save_model(self, request, obj, form, change):
        obj.save()
        if not change:
            obj.users.add(request.user)
        obj.save()
    
    def queryset(self, request):
        qs = super(MovementAdmin, self).queryset(request)
        if request.user.is_superuser or splitpath(request.META['HTTP_REFERER'])[-3]=='event':
            return qs
        return qs.filter(users=request.user)
    
    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            kwargs['fields'] = ('name','parent_work','movement_number','authors','instrumentation',
              'creation_date_start','creation_date_end','score','users','groups')
        else:
            kwargs['fields'] = ('name','parent_work','movement_number','authors','instrumentation',
              'creation_date_start','creation_date_end','score')
        return super(MovementAdmin, self).get_form(request, obj, **kwargs)

class PerformersInline(admin.StackedInline):
    
    class Media:
        js = (settings.STATIC_URL+'/grappelli/tinymce/jscripts/tiny_mce/tiny_mce_src.js',settings.STATIC_URL+'grappelli/tinymce_setup/tinymce_setup.js')
        
    fk_name = 'event'
    model = Performer
    extra = 0
    form = SortableInlineForm
    fields = ('performer','group','instruments','works','position')
    raw_id_fields = ('performer','group','instruments','works')
    autocomplete_lookup_fields = {
        'fk': ['performer','group'],
        'm2m': ['instruments','works'],
    }
    sortable_field_name = "position"
    
class ProgramInline(admin.TabularInline):
    
    class Media:
        js = (settings.STATIC_URL+'/grappelli/tinymce/jscripts/tiny_mce/tiny_mce_src.js',settings.STATIC_URL+'grappelli/tinymce_setup/tinymce_setup.js')
        
    fk_name = 'event'
    model = Program
    extra = 0
    form = SortableInlineForm
    fields = ('works' , 'program_note' , 'position',)
    raw_id_fields = ('works',)  
    autocomplete_lookup_fields = {
        'm2m': ['works'],
    }
    sortable_field_name = "position"
    inline_classes = ('collapse open',)
    
class AbstractEventAdmin(MonitorAdmin):
    
    class Media:
        js = (settings.STATIC_URL+'/grappelli/tinymce/jscripts/tiny_mce/tiny_mce_src.js',settings.STATIC_URL+'grappelli/tinymce_setup/tinymce_setup.js')
        
    raw_id_fields = ('curators','venues',)
    autocomplete_lookup_fields = {
        'm2m': ['curators','venues',],
    }
    
    ordering = ['-start_date','-start_time']
    
    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            content_type = ContentType.objects.get(app_label="thewulfcms", model=check_type(obj)).id
            mE = MonitorEntry.objects.get(content_type = content_type, object_id=obj.id)
            e = Event.objects.get(pk = obj.pk)
            mE.serialized_object = e
            mE.save()
            obj.reset_to_pending(user = request.user, notes = '')
        obj.save()
    
    def queryset(self, request):
        qs = super(AbstractEventAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs.select_subclasses()
        return qs.select_subclasses().filter(users=request.user)
    
    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            kwargs['fields'] = ('name','start_date','start_time','end_date','end_time','venues',
                                'short_description','description','curators','program_notes','raw_audio_recording','users','groups')
        else:
            kwargs['fields'] = ('name','start_date','start_time','end_date','end_time','venues',
                                'short_description','description','curators','program_notes','raw_audio_recording')
        
        if request.path == '/admin/thewulfcms/abstractevent/addevent/':
            obj = Event()
        elif request.path == '/admin/thewulfcms/abstractevent/addinstallation/':
            obj = Installation()
        return admin.site._registry[type(obj)].get_form(request, obj, **kwargs)
    
    def add_view(self, request, form_url='', extra_context=None):
        if not extra_context:
            extra_context = {}
        
        extra_context['is_abstract'] = True
        if request.path == '/admin/thewulfcms/abstractevent/addevent/':
            extra_context['type'] = 'event'
            self.inlines=[ProgramInline, PerformersInline, EventAudioInline, EventPicInline, EventVideoInline,]
            self.inline_instances=[]
            for inline_class in self.inlines:
                inline_instance = inline_class(Event, self.admin_site)
                self.inline_instances.append(inline_instance)
        elif request.path == '/admin/thewulfcms/abstractevent/addinstallation/':
            extra_context['type'] = 'installation'
            self.inlines=[ProgramInline, EventAudioInline, EventPicInline, EventVideoInline,]
            self.inline_instances=[]
            for inline_class in self.inlines:
                inline_instance = inline_class(Event, self.admin_site)
                self.inline_instances.append(inline_instance)
        return super(AbstractEventAdmin, self).add_view(request, form_url, extra_context)
    
    def change_view(self, request, object_id, extra_context=None):
        if not extra_context:
            extra_context = {}

        obj=AbstractEvent.objects.filter(id=object_id).select_subclasses()
        
        extra_context['is_abstract'] = True
        if check_type(obj[0]) == 'Event':
            extra_context['type'] = 'event'
            self.inlines=[ProgramInline, PerformersInline, EventAudioInline, EventPicInline, EventVideoInline,]
            self.inline_instances=[]
            for inline_class in self.inlines:
                inline_instance = inline_class(Event, self.admin_site)
                self.inline_instances.append(inline_instance)
        elif check_type(obj[0]) == 'Installation':
            extra_context['type'] = 'installation'
            self.inlines=[ProgramInline, EventAudioInline, EventPicInline, EventVideoInline,]
            self.inline_instances=[]
            for inline_class in self.inlines:
                inline_instance = inline_class(Event, self.admin_site)
                self.inline_instances.append(inline_instance)
        return super(AbstractEventAdmin, self).change_view(request, object_id, extra_context)
    
    def changelist_view(self, request, extra_context=None):
        if not extra_context:
            extra_context = {}
        
        extra_context['is_abstract'] = True
        extra_context['children'] = ['event','installation',]
        return super(AbstractEventAdmin, self).changelist_view(request, extra_context)
    
    def get_urls(self):
        urls = super(AbstractEventAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^addevent/$', self.admin_site.admin_view(self.add_view)),
            (r'^addinstallation/$', self.admin_site.admin_view(self.add_view)),
        )
        return my_urls + urls
    
#from django.forms.models import ModelForm, model_to_dict
#from moderation.models import MODERATION_STATUS_PENDING,\
#    MODERATION_STATUS_REJECTED
#from django.core.exceptions import ObjectDoesNotExist
    
class EventAdmin(MonitorAdmin):
    
    class Media:
        js = (settings.STATIC_URL+'/grappelli/tinymce/jscripts/tiny_mce/tiny_mce_src.js',settings.STATIC_URL+'grappelli/tinymce_setup/tinymce_setup.js')
     
    fields = ('name','start_date','start_time','end_date','end_time','venues',
              'short_description','description','curators','program_notes',
              'raw_audio_recording',
              'users','groups')
    readonly_fields = (
                       'raw_audio_recording',
                       'start_date','start_time','end_date','end_time','venues','users','groups')
    
    inlines = [ProgramInline, PerformersInline, EventAudioInline, EventPicInline, EventVideoInline,]
    raw_id_fields = ('curators','venues',)
    autocomplete_lookup_fields = {
        'm2m': ['curators','venues',],
    }
    
    ordering = ['-start_date','-start_time']
#    list_display = ('start_date', 'name')
    
    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            content_type = ContentType.objects.get(app_label="thewulfcms", model=check_type(obj)).id
            mE = MonitorEntry.objects.get(content_type = content_type, object_id=obj.id)
            e = Event.objects.get(pk = obj.pk)
            mE.serialized_object = e
            mE.save()
            obj.reset_to_pending(user = request.user, notes = '')
        obj.save()
    
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        else:
            return (
                       'raw_audio_recording',
                       'start_date','start_time','end_date','end_time','venues','users','groups')
    
    def queryset(self, request):
        qs = super(EventAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(users=request.user)
    
    def get_form(self, request, obj=None, **kwargs):
        
#        instance = kwargs.get('instance', None)
#
#        if instance:
#            try:
#                if instance.moderated_object.moderation_status in\
#                   [MODERATION_STATUS_PENDING, MODERATION_STATUS_REJECTED] and\
#                   not instance.moderated_object.moderator.\
#                   visible_until_rejected:
#                    initial =\
#                    model_to_dict(instance.moderated_object.changed_object)
#                    kwargs.setdefault('initial', {})
#                    kwargs['initial'].update(initial)
#            except ObjectDoesNotExist:
#                pass
            
            
        if request.user.is_superuser:
            kwargs['fields'] = ('name','start_date','start_time','end_date','end_time','venues',
                                'short_description','description','curators','program_notes','raw_audio_recording','users','groups')
        else:
            kwargs['fields'] = ('name','start_date','start_time','end_date','end_time','venues',
                                'short_description','description','curators','program_notes','raw_audio_recording')
        return super(EventAdmin, self).get_form(request, obj, **kwargs)

    
    
class InstallationAdmin(MonitorAdmin):
    
    class Media:
        js = (settings.STATIC_URL+'/grappelli/tinymce/jscripts/tiny_mce/tiny_mce_src.js',settings.STATIC_URL+'grappelli/tinymce_setup/tinymce_setup.js')
        
    fields = ('name','start_date','start_time','end_date','end_time','venues',
              'short_description','description','curators','program_notes','users','groups')
    readonly_fields = ('start_date','start_time','end_date','end_time','venues','users','groups')
    
    inlines = [ProgramInline, EventAudioInline, EventPicInline, EventVideoInline,]
    raw_id_fields = ('curators','venues',)
    autocomplete_lookup_fields = {
        'm2m': ['curators','venues',],
    }
    
    ordering = ['-start_date','-start_time']
    
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        else:
            return ('start_date','start_time','end_date','end_time','venues','users','groups')
    
    def queryset(self, request):
        qs = super(InstallationAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(users=request.user)
    
    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            kwargs['fields'] = ('name','start_date','start_time','end_date','end_time','venues',
                                'short_description','description','curators','program_notes','users','groups')
        else:
            kwargs['fields'] = ('name','start_date','start_time','end_date','end_time','venues',
                                'short_description','description','curators','program_notes')
        return super(InstallationAdmin, self).get_form(request, obj, **kwargs)

class AbstractProfileAdmin(MonitorAdmin):
    
    class Media:
        js = (settings.STATIC_URL+'/grappelli/tinymce/jscripts/tiny_mce/tiny_mce_src.js',settings.STATIC_URL+'grappelli/tinymce_setup/tinymce_setup.js')
        
    # is it possible to do primary_instruments since that is at the SingleProfile level
    raw_id_fields = ('emails','weblinks')
    autocomplete_lookup_fields = {
        'm2m': ['emails','weblinks'],
    }
    inlines = [ProfilePicInline, ProfileVideoInline,ProfileAudioInline]
    
    ordering = ['name']
    
#    actions = ['delete_model']
#    
#    def get_actions(self, request):
#        actions = super(AbstractProfileAdmin, self).get_actions(request)
#        del actions['delete_selected']
#        return actions
#
#    def delete_model(self, request, obj):
#        for o in obj.all():
#            delObj=AbstractProfile.objects.filter(id=o.id).select_subclasses()
#            delObj.delete()
#    
#    delete_model.short_description = 'Delete flow'
    
#    def has_add_permission(self, request):
#        if request.path == '/admin/thewulfcms/abstractprofile/add/':
#            False
#        else:
#            True
    
    def save_model(self, request, obj, form, change):
        obj.save()
        if not change:
            obj.users.add(request.user)
        obj.save()
    
    def queryset(self, request):
        qs = super(AbstractProfileAdmin, self).queryset(request)
        testlist = ['event', 'abstractevent', 'installation', 'work', 'abstractwork', 'installation']
        if request.user.is_superuser or splitpath(request.META['HTTP_REFERER'])[-3] in testlist:
            return qs.select_subclasses()
        return qs.select_subclasses().filter(users=request.user)
    
    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            kwargs['fields'] = ('name','address_1','address_2','city','state','country','zip_code',
                                'phone_number_1','phone_number_2','birth_date','death_date',
                                'emails','weblinks','primary_instruments',
                                'short_description','description',
                                'is_author','is_performer','is_member','mailing_list_optout',
                                'users','groups')
        else:
            kwargs['fields'] = ('name','address_1','address_2','city','state','country','zip_code',
                                'phone_number_1','phone_number_2','birth_date','death_date',
                                'emails','weblinks','primary_instruments',
                                'short_description','description',
                                'is_author','is_performer','is_member','mailing_list_optout')
        
        if request.path == '/admin/thewulfcms/abstractprofile/addsingleprofile/':
            obj = SingleProfile()
        elif request.path == '/admin/thewulfcms/abstractprofile/addgroupprofile/':
            obj = GroupProfile()
        elif request.path == '/admin/thewulfcms/abstractprofile/addvenueprofile/':
            obj = VenueProfile()
        return admin.site._registry[type(obj)].get_form(request, obj, **kwargs)
    
    def add_view(self, request, form_url='', extra_context=None):
        if not extra_context:
            extra_context = {}
        
        extra_context['is_abstract'] = True
        if request.path == '/admin/thewulfcms/abstractprofile/addsingleprofile/':
            extra_context['type'] = 'singleprofile'
        elif request.path == '/admin/thewulfcms/abstractprofile/addgroupprofile/':
            extra_context['type'] = 'groupprofile'
        elif request.path == '/admin/thewulfcms/abstractprofile/addvenueprofile/':
            extra_context['type'] = 'venueprofile'
        return super(AbstractProfileAdmin, self).add_view(request, form_url, extra_context)
    
    
    
    def changelist_view(self, request, extra_context=None):
        if not extra_context:
            extra_context = {}
        
        extra_context['is_abstract'] = True
        extra_context['children'] = ['singleprofile','groupprofile','venueprofile',]
        return super(AbstractProfileAdmin, self).changelist_view(request, extra_context)
    
    def get_urls(self):
        urls = super(AbstractProfileAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^addsingleprofile/$', self.admin_site.admin_view(self.add_view)),
            (r'^addgroupprofile/$', self.admin_site.admin_view(self.add_view)),
            (r'^addvenueprofile/$', self.admin_site.admin_view(self.add_view))
        )
        return my_urls + urls
    
class SingleProfileAdmin(MonitorAdmin):
    
    class Media:
        js = (settings.STATIC_URL+'/grappelli/tinymce/jscripts/tiny_mce/tiny_mce_src.js',settings.STATIC_URL+'grappelli/tinymce_setup/tinymce_setup.js')
        
    raw_id_fields = ('weblinks','emails','primary_instruments')
    autocomplete_lookup_fields = {
        'm2m': ['weblinks','emails','primary_instruments'],
    }
    
    ordering = ['name']
    
    readonly_fields = ()
    
    def queryset(self, request):
        qs = super(SingleProfileAdmin, self).queryset(request)
        testlist = ['event', 'abstractevent', 'installation', 'groupprofile']
        if request.user.is_superuser or splitpath(request.META['HTTP_REFERER'])[-3] in testlist:
            return qs
        return qs.filter(users=request.user)
    
    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            kwargs['fields'] = ('name','address_1','address_2','city','state','country','zip_code',
                                'phone_number_1','phone_number_2','birth_date','death_date',
                                'emails','weblinks','primary_instruments',
                                'short_description','description',
                                'is_author','is_performer','is_member','mailing_list_optout',
                                'users','groups')
        else:
            kwargs['fields'] = ('name','address_1','address_2','city','state','country','zip_code',
                                'phone_number_1','phone_number_2','birth_date','death_date',
                                'emails','weblinks','primary_instruments',
                                'short_description','description',
                                'is_author','is_performer','is_member','mailing_list_optout')
        return super(SingleProfileAdmin, self).get_form(request, obj, **kwargs)
    inlines = [ProfilePicInline, ProfileVideoInline,ProfileAudioInline]
    
class GroupProfileAdmin(MonitorAdmin):
    
    class Media:
        js = (settings.STATIC_URL+'/grappelli/tinymce/jscripts/tiny_mce/tiny_mce_src.js',settings.STATIC_URL+'grappelli/tinymce_setup/tinymce_setup.js')
        
    raw_id_fields = ('members','weblinks','emails')
    autocomplete_lookup_fields = {
        'm2m': ['members','weblinks','emails'],
    }
    
    ordering = ['name']
    
    readonly_fields = ()
    
    def queryset(self, request):
        qs = super(GroupProfileAdmin, self).queryset(request)
        testlist = ['event', 'abstractevent', 'installation']
        if request.user.is_superuser or splitpath(request.META['HTTP_REFERER'])[-3] in testlist:
            return qs
        return qs.filter(users=request.user)
    
    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            kwargs['fields'] = ('name','members','address_1','address_2','city','state','country','zip_code',
                                'phone_number_1','phone_number_2','birth_date','death_date',
                                'emails','weblinks',
                                # why not primary instruments for groups?
#                                'primary_instruments',
                                'short_description','description',
                                'is_member','mailing_list_optout',
                                'users','groups')
        else:
            kwargs['fields'] = ('name','members','address_1','address_2','city','state','country','zip_code',
                                'phone_number_1','phone_number_2','birth_date','death_date',
                                'emails','weblinks',
                                # why not primary instruments for groups?
#                                'primary_instruments',
                                'short_description','description',
                                'is_member','mailing_list_optout')
        return super(GroupProfileAdmin, self).get_form(request, obj, **kwargs)
    inlines = [ProfilePicInline, ProfileVideoInline,ProfileAudioInline]
    
class VenueProfileAdmin(MonitorAdmin):
    
    class Media:
        js = (settings.STATIC_URL+'/grappelli/tinymce/jscripts/tiny_mce/tiny_mce_src.js',settings.STATIC_URL+'grappelli/tinymce_setup/tinymce_setup.js')
        
    raw_id_fields = ('weblinks','emails')
    autocomplete_lookup_fields = {
        'm2m': ['weblinks','emails'],
    }
    
    ordering = ['name']
    
    readonly_fields = ()
    
    def queryset(self, request):
        qs = super(VenueProfileAdmin, self).queryset(request)
        testlist = ['event', 'abstractevent', 'installation']
        if request.user.is_superuser or splitpath(request.META['HTTP_REFERER'])[-3] in testlist:
            return qs
        return qs.filter(users=request.user)
    
    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            kwargs['fields'] = ('name','address_1','address_2','city','state','country','zip_code',
                                'phone_number_1','phone_number_2','birth_date','death_date',
                                'emails','weblinks',
                                # why not primary instruments for groups?
#                                'primary_instruments',
                                'short_description','description',
                                'is_member','mailing_list_optout',
                                'users','groups')
        else:
            kwargs['fields'] = ('name','address_1','address_2','city','state','country','zip_code',
                                'phone_number_1','phone_number_2','birth_date','death_date',
                                'emails','weblinks',
                                # why not primary instruments for groups?
#                                'primary_instruments',
                                'short_description','description',
                                'is_member','mailing_list_optout')
        return super(VenueProfileAdmin, self).get_form(request, obj, **kwargs)
    
    def get_model_perms(self, request):
        """
        Return empty perms dict if not superuser thus hiding the model from admin index.
        """
        if request.user.is_superuser:
            return {
            'add': self.has_add_permission(request),
            'change': self.has_change_permission(request),
            'delete': self.has_delete_permission(request),
            }
        else:
            return {}
        
    inlines = [ProfilePicInline, ProfileVideoInline,ProfileAudioInline]
    
class InstrumentAdmin(MonitorAdmin):
    
    class Media:
        js = (settings.STATIC_URL+'/grappelli/tinymce/jscripts/tiny_mce/tiny_mce_src.js',settings.STATIC_URL+'grappelli/tinymce_setup/tinymce_setup.js')
    
    def queryset(self, request):
        qs = super(InstrumentAdmin, self).queryset(request)
        testlist = ['event', 'abstractevent', 'installation','work', 'movement','abstractwork']
        if request.user.is_superuser or splitpath(request.META['HTTP_REFERER'])[-3] in testlist:
            return qs
        return qs.filter(users=request.user)
    
    def save_model(self, request, obj, form, change):
        obj.save()
        if not change:
            obj.users.add(request.user)
        obj.save()
        
    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            kwargs['fields'] = ('name','short_description','description','users','groups')
        else:
            kwargs['fields'] = ('name','short_description','description')
        return super(InstrumentAdmin, self).get_form(request, obj, **kwargs)
    
    
class PostAdmin(MonitorAdmin):
    
    class Media:
        js = (settings.STATIC_URL+'/grappelli/tinymce/jscripts/tiny_mce/tiny_mce_src.js',settings.STATIC_URL+'grappelli/tinymce_setup/tinymce_setup.js')
        
    raw_id_fields = ('category',)
    autocomplete_lookup_fields = {
        'm2m': ['category'],
    }
    
    readonly_fields = ()
    
    def queryset(self, request):
        qs = super(PostAdmin, self).queryset(request)
        testlist = []
        if request.user.is_superuser or splitpath(request.META['HTTP_REFERER'])[-3] in testlist:
            return qs
        return qs.filter(users=request.user)
    
    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            kwargs['fields'] =  ('name','category','short_description','description','users','groups',)
        else:
            kwargs['fields'] =  ('name','category','short_description','description','category',)
        return super(PostAdmin, self).get_form(request, obj, **kwargs)
    inlines = [PostPicInline, PostVideoInline,PostAudioInline]
        
        
class CategoryAdmin(MonitorAdmin):
    
    class Media:
        js = (settings.STATIC_URL+'/grappelli/tinymce/jscripts/tiny_mce/tiny_mce_src.js',settings.STATIC_URL+'grappelli/tinymce_setup/tinymce_setup.js')
    
    def queryset(self, request):
        qs = super(CategoryAdmin, self).queryset(request)
        testlist = ['post']
        if request.user.is_superuser or splitpath(request.META['HTTP_REFERER'])[-3] in testlist:
            return qs
        return qs.filter(users=request.user)
    
    def save_model(self, request, obj, form, change):
        obj.save()
        if not change:
            obj.users.add(request.user)
        obj.save()
        
    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            kwargs['fields'] = ('name','short_description','description','users','groups')
        else:
            kwargs['fields'] = ('name','short_description','description')
        return super(CategoryAdmin, self).get_form(request, obj, **kwargs)
    
    
class HiddenModelsAdmin(MonitorAdmin):
    def get_model_perms(self, request):
        """
        Return empty perms dict if not superuser thus hiding the model from admin index.
        """
        if request.user.is_superuser:
            return {
            'add': self.has_add_permission(request),
            'change': self.has_change_permission(request),
            'delete': self.has_delete_permission(request),
            }
        else:
            return {}
  
admin.site.register(AbstractEvent, AbstractEventAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Installation, InstallationAdmin)
admin.site.register(AbstractWork, AbstractWorkAdmin)
admin.site.register(Work, WorkAdmin)
admin.site.register(Movement, MovementAdmin)
admin.site.register(Instrument, InstrumentAdmin)

admin.site.register(AbstractProfile, AbstractProfileAdmin)
admin.site.register(SingleProfile, SingleProfileAdmin)
admin.site.register(GroupProfile, GroupProfileAdmin)
admin.site.register(VenueProfile, VenueProfileAdmin)

#admin.site.register(User, HiddenModelsAdmin)
admin.site.register(Performer, HiddenModelsAdmin)
admin.site.register(Program, HiddenModelsAdmin)
admin.site.register(Weblink, HiddenModelsAdmin)
#admin.site.register(Instrument, HiddenModelsAdmin)

admin.site.register(EventAudioRecording, HiddenModelsAdmin)
admin.site.register(EventVideo, HiddenModelsAdmin)
admin.site.register(EventPic, HiddenModelsAdmin)

admin.site.register(ProfileAudioRecording, HiddenModelsAdmin)
admin.site.register(ProfileVideo, HiddenModelsAdmin)
admin.site.register(ProfilePic, HiddenModelsAdmin)

admin.site.register(PostAudioRecording, HiddenModelsAdmin)
admin.site.register(PostVideo, HiddenModelsAdmin)
admin.site.register(PostPic, HiddenModelsAdmin)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Email, HiddenModelsAdmin)