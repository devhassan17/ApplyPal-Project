from django.contrib import admin

from .models import  Iframe, Visitor, Appointment, Analytics,University

admin.site.register(University)
admin.site.register(Iframe)
admin.site.register(Visitor)
admin.site.register(Appointment)
admin.site.register(Analytics)

