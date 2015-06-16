from django import forms
from models import *
#from django.forms import fields, models, widgets, ModelForm
#from django.contrib.auth.models import User
#from django.contrib.auth.forms import UserCreationForm
#from django.contrib.formtools.wizard import FormWizard
#from django.utils.encoding import force_unicode
#from django.contrib.admin import widgets
#from admin import EventAdmin, PerformanceAdmin, EPIP_LnkAdmin

class SortableInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SortableInlineForm, self).__init__(*args, **kwargs)
        self.fields['position'].widget = forms.HiddenInput()
        self.fields['position'].label = ''
    
        

#class EventForm(ModelForm):
#    class Meta:
#        model = Event
#    def __init__(self, *args, **kwargs):
#        super(EventForm, self).__init__(*args, **kwargs)
#        self.fields['start_date'].widget = widgets.AdminDateWidget()
#        self.fields['start_time'].widget = widgets.AdminTimeWidget()
#
#class PerformanceForm(ModelForm):
#    class Meta:
#        model = Performance
#
#class Performance_Performer_Instrument_LnkForm(ModelForm):
#    class Meta:
#        model = Performance_Performer_Instrument_Lnk
#
#
#class EventCreationWizard(FormWizard):
#
#    @property
#    def __name__(self):
#        # Python instances don't define __name__ (though functions and classes do).
#        # We need to define this, otherwise the call to "update_wrapper" fails:
#        return self.__class__.__name__
#
##    def get_template(self, step):
##        # Optional: return the template used in rendering this wizard:
##        return 'admin/testapp/employer/wizard.html'
#
#    def parse_params(self, request, admin=None, *args, **kwargs):
#        # Save the ModelAdmin instance so it's available to other methods:
#        self._model_admin = admin
#        # The following context variables are expected by the admin
#        # "change_form.html" template; Setting them enables stuff like
#        # the breadcrumbs to "just work":
#        opts = admin.model._meta
#        self.extra_context.update({
#            'title': 'Add %s' % force_unicode(opts.verbose_name),
#            # See http://docs.djangoproject.com/en/dev/ref/contrib/admin/#adding-views-to-admin-sites
#            # for why we define this variable.
#            'current_app': admin.admin_site.name,
#            'has_change_permission': admin.has_change_permission(request),
#            'add': True,
#            'opts': opts,
#            'root_path': admin.admin_site.root_path,
#            'app_label': opts.app_label,
#        })
#
#    def render_template(self, request, form, previous_fields, step, context=None):
#        from django.contrib.admin.helpers import AdminForm
#        # Wrap this form in an AdminForm so we get the fieldset stuff:
#        form = AdminForm(form, [(
#            'Step %d of %d' % (step + 1, self.num_steps()),
#            {'fields': form.base_fields.keys()}
#            )], {})
#        context = context or {}
#        context.update({
#            'media': self._model_admin.media + form.media
#        })
#        return super(EventCreationWizard, self).render_template(request, form, previous_fields, step, context)
#
#    def process_step(self, request, form, step):
#        form.save()
#        
#        
##    def done(self, request, form_list):
##        data = {}
##        for form in form_list:
##            data.update(form.cleaned_data)
##        # First, create user:
##        user = User.objects.create(
##            username=data['username'],
##            first_name=data['first_name'],
##            last_name=data['last_name'],
##            email=data['email']
##        )
##        user.set_password(data['password1'])
##        user.save()
##        # Next, create employer:
##        employer = Employer.objects.create(
##            user=user,
##            company_name=data['company_name'],
##            address=data['address'],
##            company_description=data.get('company_description', ''),
##            website=data.get('website', '')
##        )
##        # Display success message and redirect to changelist:
##        return self._model_admin.response_add(request, employer)
#
#create_event = EventCreationWizard([EventForm, PerformanceForm, Performance_Performer_Instrument_LnkForm])
