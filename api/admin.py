from django.contrib import admin

from api.models import Job, UserProfile, JobApplication, ChatRoom, Message, Comment

# Register your models here.
admin.site.register(Job)
admin.site.register(UserProfile)
admin.site.register(JobApplication)
admin.site.register(ChatRoom)
admin.site.register(Message)
admin.site.register(Comment)