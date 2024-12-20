from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Job, UserProfile, JobApplication, ChatRoom, Message, Comment


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'location', 'latitude', 'longitude', 'price', 'posted_by', 'taken_by', 'created_at']
        read_only_fields = ['posted_by', 'taken_by', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        print(validated_data)
        user = User.objects.create_user(**validated_data)
        return user

class JobApplicationSerializer(serializers.ModelSerializer):
    job = JobSerializer()
    applicant = serializers.StringRelatedField()  # or UserSerializer if you want detailed user info
    phone_number = serializers.CharField(source='applicant.userprofile.phone_number', read_only=True)
    applicant_name = serializers.CharField(source='applicant.username', read_only=True)

    class Meta:
        model = JobApplication
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'name', 'surname', 'birthdate', 'email', 'phone_number', 'job_description', 'jobs_done', 'jobs_posted', 'rating']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'chat_room', 'sender', 'content', 'timestamp']

class ChatRoomSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    class Meta:
        model = ChatRoom
        fields = ['id', 'job', 'participants', 'messages']

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'job', 'author', 'author_username', 'text', 'created_at']
        read_only_fields = ['author', 'created_at']