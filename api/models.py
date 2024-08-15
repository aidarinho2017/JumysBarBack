from django.db import models
from django.contrib.auth.models import User

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
    CATEGORY_CHOICES = [
        ('babysitting', 'Babysitting'),
        ('cleaning', 'Cleaning'),
        ('teaching', 'Teaching'),
        ('other', 'Other')
    ]
    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    posted_by = models.ForeignKey(User, related_name='posted_jobs', on_delete=models.CASCADE)
    taken_by = models.ForeignKey(User, related_name='taken_jobs', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class JobApplication(models.Model):
    job = models.ForeignKey(Job, related_name='applications', on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, related_name='applications', on_delete=models.CASCADE)
    suggested_price = models.FloatField(default=0.0)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('denied', 'Denied')], default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.job.title

class ChatRoom(models.Model):
    job = models.ForeignKey(Job, related_name='chat_rooms', on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name='chat_rooms')

    def __str__(self):
        return f"ChatRoom for Job: {self.job.title}"

class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"

class Comment(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)