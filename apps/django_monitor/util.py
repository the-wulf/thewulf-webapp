
from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.db.models import Manager

from django_monitor.middleware import get_current_user
from django_monitor.models import MonitorEntry, MONITOR_TABLE
from django_monitor.conf import (
    STATUS_DICT, PENDING_STATUS, APPROVED_STATUS, CHALLENGED_STATUS
)

def create_moderate_perms(app, created_models, verbosity, **kwargs):
    """ This will create moderate permissions for all registered models"""
    from django.contrib.auth.models import Permission

    from django_monitor import queued_models

    for model in queued_models():
        ctype = ContentType.objects.get_for_model(model)
        codename = 'moderate_%s' % model._meta.object_name.lower()
        name = u'Can moderate %s' % model._meta.verbose_name_raw
        p, created = Permission.objects.get_or_create(
            codename = codename,
            content_type__pk = ctype.id,
            defaults = {'name': name, 'content_type': ctype}
        )
        if created and verbosity >= 2:
            print "Adding permission '%s'" % p

def add_fields(cls, manager_name, status_name, monitor_name, base_manager):
    """ Add additional fields like status to moderated models"""
    # Inheriting from old manager
    if base_manager is None:
        if hasattr(cls, manager_name):
            base_manager = getattr(cls, manager_name).__class__
        else:
            base_manager = Manager
    # Queryset inheriting from manager's Queryset
    base_queryset = base_manager().get_query_set().__class__

    class CustomQuerySet(base_queryset):
        """ Chainable queryset for checking status """
       
        def _by_status(self, field_name, status):
            """ Filter queryset by given status"""
            where_clause = '%s = %%s' % (field_name)
            return self.extra(where = [where_clause], params = [status])

        def approved(self):
            """ All approved objects"""
            return self._by_status(status_name, APPROVED_STATUS)

        def exclude_approved(self):
            """ All not-approved objects"""
            where_clause = '%s != %%s' % (status_name)
            return self.extra(
                where = [where_clause], params = [APPROVED_STATUS]
            )

        def pending(self):
            """ All pending objects """
            return self._by_status(status_name, PENDING_STATUS)

        def challenged(self):
            """ All challenged objects """
            return self._by_status(status_name, CHALLENGED_STATUS)

    class CustomManager(base_manager):
        """ custom manager that adds parameters and uses custom QuerySet """

        # use_for_related_fields is read when the model class is prepared
        # because CustomManager isn't set on the class at the time
        # this really has no effect, but is set to True because we are going
        # to hijack cls._default_manager later
        use_for_related_fields = True

        # add monitor_id and status_name attributes to the query
        def get_query_set(self):
            # parameters to help with generic SQL
            db_table = self.model._meta.db_table
            pk_name = self.model._meta.pk.attname
            content_type = ContentType.objects.get_for_model(self.model).id
            
            # extra params - status and id of object (for later access)
            select = {
                '_monitor_id': '%s.id' % MONITOR_TABLE,
                '_status': '%s.status' % MONITOR_TABLE,
            }
            where = [
                '%s.content_type_id=%s' % (MONITOR_TABLE, content_type),
                '%s.object_id=%s.%s' % (MONITOR_TABLE, db_table, pk_name)
            ]
            tables = [MONITOR_TABLE]

            # build extra query then copy model/query to a CustomQuerySet
            q = super(CustomManager, self).get_query_set().extra(
                select = select, where = where, tables = tables
            )
            return CustomQuerySet(self.model, q.query)

        def __getattr__(self, attr):
            """ Try to get the rest of attributes from queryset """
            try:
                return getattr(self, attr)
            except AttributeError:
                return getattr(self.get_query_set(), attr)

    def _get_monitor_status(self):
        """
        Accessor for monitor_status.
        To be added to the model as a property, ``monitor_status``.
        """
        if not hasattr(self, '_status'):
            return getattr(self, monitor_name).status
        return self._status

    def _get_monitor_entry(self):
        """ accessor for monitor_entry that caches the object """
        if not hasattr(self, '_monitor_entry'):
            self._monitor_entry = MonitorEntry.objects.get_for_instance(self)
        return self._monitor_entry
    
    def _get_monitor_serialized_object(self):
        """
        Accessor for monitor_serialized_object.
        To be added to the model as a property, ``monitor_serialized_object``.
        """
        if not hasattr(self, '_serialized_object'):
            return getattr(self, monitor_name).serialized_object
        return self._serialized_object

    def _get_status_display(self):
        """ to display the moderation status in verbose """
        return STATUS_DICT[self.monitor_status]
    _get_status_display.short_description = status_name

    def moderate(self, status, user = None, notes = ''):
        """ developers may use this to moderate objects """
        import django_monitor
        getattr(self, monitor_name).moderate(status, user, notes)
        # Auto-Moderate parents also
        monitored_parents = filter(
            lambda x: django_monitor.model_from_queue(x),
            self._meta.parents.keys()
        )
        for parent in monitored_parents:
            parent_ct = ContentType.objects.get_for_model(parent)
            parent_pk_field = self._meta.get_ancestor_link(parent)
            parent_pk = getattr(self, parent_pk_field.attname)
            me = MonitorEntry.objects.get(
                content_type = parent_ct, object_id = parent_pk
            )
            me.moderate(status, user)

    def approve(self, user = None, notes = ''):
        """ Approve the object & its parents."""
        self.moderate(APPROVED_STATUS, user, notes)

    def challenge(self, user = None, notes = ''):
        """Challenge"""
        self.moderate(CHALLENGED_STATUS, user, notes)

    def reset_to_pending(self, user = None, notes = ''):
        """Reset"""
        self.moderate(PENDING_STATUS, user, notes)

    def is_approved(self):
        return self.monitor_status == APPROVED_STATUS

    def is_pending(self):
        return self.monitor_status == PENDING_STATUS

    def is_challenged(self):
        return self.monitor_status == CHALLENGED_STATUS

    # Add custom manager & monitor_entry to class
    manager = CustomManager()
    cls.add_to_class(manager_name, manager)
    cls.add_to_class(monitor_name, property(_get_monitor_entry))
    cls.add_to_class('monitor_status', property(_get_monitor_status)) 
    cls.add_to_class('monitor_serialized_object', property(_get_monitor_serialized_object)) 
    cls.add_to_class(status_name, lambda self: self.monitor_status)
    cls.add_to_class(
        'get_monitor_status_display', _get_status_display
    )
    cls.add_to_class('moderate', moderate)
    cls.add_to_class('approve', approve)
    cls.add_to_class('challenge', challenge)
    cls.add_to_class('reset_to_pending', reset_to_pending)
    cls.add_to_class('is_approved', property(is_approved))
    cls.add_to_class('is_challenged', property(is_challenged))
    cls.add_to_class('is_pending', property(is_pending))
    # We have a custom filter defined in django_monitor.filter to enable
    # filtering of model objects by their moderation status.
    # But `status` is not a real field and Django does not support filters
    # on non-fields as of now. Our way out is to attach the filter to some
    # other field which the developer may never include in ``list_filter``.

    # Used ``pk`` before but subclassed models raise FieldDoesNotExist here.
    # So let's use ``id``. Latest Django dev-version has undergone changes to
    # allow non-fields. So this hack must be for a short period of time.
    cls._meta.get_field('id').monitor_filter = True

    # Copy manager to default_class
    cls._default_manager = manager

def save_handler(sender, instance, **kwargs):
    """
    The following things are done after creating an object in moderated class:
    1. Creates monitor entries for object and its parents.
    2. Auto-approves object, its parents & specified related objects if user 
       has ``moderate`` permission. Otherwise, they are put in pending.
    """
    import django_monitor
    # Auto-moderation
    user = get_current_user()
    opts = instance.__class__._meta
    mod_perm = '%s.moderate_%s' % (
        opts.app_label.lower(), opts.object_name.lower()
    )
    if user and user.has_perm(mod_perm):
        status = APPROVED_STATUS
    else:
        status = PENDING_STATUS

    # Create corresponding monitor entry
    if kwargs.get('created', None):
        me = MonitorEntry.objects.create(
            status = status,
            content_object = instance,
            timestamp = datetime.now()
        )
        me.moderate(status, user)

        # Create one monitor_entry per moderated parent.
        monitored_parents = filter(
            lambda x: django_monitor.model_from_queue(x),
            instance._meta.parents.keys()
        )
        for parent in monitored_parents:
            parent_ct = ContentType.objects.get_for_model(parent)
            parent_pk_field = instance._meta.get_ancestor_link(parent)
            parent_pk = getattr(instance, parent_pk_field.attname)
            try:
                me = MonitorEntry.objects.get(
                    content_type = parent_ct, object_id = parent_pk
                )
            except MonitorEntry.DoesNotExist:
                me = MonitorEntry(
                    content_type = parent_ct, object_id = parent_pk,
                )
            me.moderate(status, user)

        # Moderate related objects too... 
        model = django_monitor.model_from_queue(instance.__class__)
        if model:
            for rel_name in model['rel_fields']:
                rel_obj = getattr(instance, rel_name, None)
                if rel_obj:
                    moderate_rel_objects(rel_obj, status, user)

def moderate_rel_objects(given, status, user = None):
    """
    `given` can either be any model object or a queryset. Moderate given
    object(s) and all specified related objects.
    TODO: Permissions must be checked before each iteration.
    """
    from django_monitor import model_from_queue
    # Not sure how we can find whether `given` is a queryset or object.
    # Now assume `given` is a queryset/related_manager if it has 'all'
    if not given:
        # given may become None. Stop there.
        return
    if hasattr(given, 'all'):
        qset = given.all()
        for obj in qset:
            obj.moderate(status, user)
            model = model_from_queue(qset.model)
            if model:
                for rel_name in model['rel_fields']:
                    rel_obj = getattr(obj, rel_name, None)
                    if rel_obj:
                        moderate_rel_objects(rel_obj, status, user)
    else:
        given.moderate(status, user)
        model = model_from_queue(given.__class__)
        if model:
            for rel_name in model['rel_fields']:
                rel_obj = getattr(given, rel_name, None)
                if rel_obj:
                    moderate_rel_objects(rel_obj, status, user)

def delete_handler(sender, instance, **kwargs):
    """ When an instance is deleted, delete corresponding monitor_entries too"""
    from django_monitor import model_from_queue
    if model_from_queue(sender):
        me = MonitorEntry.objects.get_for_instance(instance)
        if me:
            me.delete()
        # Delete monitor_entries of parents too
        monitored_parents = filter(
            lambda x: model_from_queue(x),
            instance._meta.parents.keys()
        )
        for parent in monitored_parents:
            parent_ct = ContentType.objects.get_for_model(parent)
            parent_pk_field = instance._meta.get_ancestor_link(parent)
            parent_pk = getattr(instance, parent_pk_field.attname)
            try:
                me = MonitorEntry.objects.get(
                    content_type = parent_ct, object_id = parent_pk
                )
                me.delete()
            except MonitorEntry.DoesNotExist:
                pass
