from django.db import models
from django.contrib.auth.models import User
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="myGeocoder")

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    surname = models.CharField(max_length=100, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    job_description = models.TextField(blank=True)
    jobs_done = models.IntegerField(default=0)
    jobs_posted = models.IntegerField(default=0)
    rating = models.FloatField(default=0)

    def __str__(self):
        return self.user.username

class Job(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    posted_by = models.ForeignKey(User, related_name='posted_jobs', on_delete=models.CASCADE)
    taken_by = models.ForeignKey(User, related_name='taken_jobs', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class JobApplication(models.Model):
    job = models.ForeignKey(Job, related_name='applications', on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, related_name='applications', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('denied', 'Denied')], default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.job.title