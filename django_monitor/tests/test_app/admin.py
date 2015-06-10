from django.contrib import admin

from django_monitor.tests.test_app.models import (
    Author, Book, EBook, Supplement, Publisher, Reader
)
from django_monitor.admin import MonitorAdmin

class AuthorAdmin(MonitorAdmin):
    """ Monitored model. So the admin inherited from MonitorAdmin."""
    list_display = ('__unicode__',)

class SuppInline(admin.TabularInline):
    model = Supplement
    fk_name = 'book'
    extra = 2

class BookAdmin(MonitorAdmin):
    inlines = [SuppInline,]

class EBookAdmin(MonitorAdmin):
    inlines = [SuppInline,]

class PubAdmin(admin.ModelAdmin):
    """ Model not monitored. Use the built-in admin"""
    pass

class ReaderAdmin(MonitorAdmin):
    """ To test the custom queryset """

    def queryset(self, request):
        """ Returns the reader that corresponds to user"""
        qset = super(ReaderAdmin, self).queryset(request)
        return qset.filter(user = request.user)

admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(EBook, EBookAdmin)
admin.site.register(Publisher, PubAdmin)
admin.site.register(Reader, ReaderAdmin)

