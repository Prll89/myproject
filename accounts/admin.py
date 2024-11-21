from django.contrib import admin
from .models import ProcessedFile, Contact, Study

class ProcessedFileAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'user', 'upload_date')

class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')

admin.site.register(ProcessedFile, ProcessedFileAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Study)
