from django.contrib import admin

from .models import University, UniversityAdmin, Iframe, Visitor, Appointment, Analytics

admin.site.register(University)
admin.site.register(UniversityAdmin)
admin.site.register(Iframe)
admin.site.register(Visitor)
admin.site.register(Appointment)
admin.site.register(Analytics)

