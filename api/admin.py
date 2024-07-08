from django.contrib import admin

from api.models import Job, UserProfile, JobApplication

# Register your models here.
admin.site.register(Job)
admin.site.register(UserProfile)
admin.site.register(JobApplication)