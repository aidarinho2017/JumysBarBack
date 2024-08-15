from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from rest_framework.views import APIView

from .models import Job, UserProfile, JobApplication, ChatRoom, Message, Comment
from .permissions import IsJobCreatorOrApplicant
from .serializers import JobSerializer, UserSerializer, UserProfileSerializer, JobApplicationSerializer, \
    ChatRoomSerializer, MessageSerializer, CommentSerializer


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get', 'put'])
    def me(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        if request.method == 'PUT':
            serializer = self.get_serializer(profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = self.get_serializer(profile)
            return Response(serializer.data)

class UserProfileRetrieveUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return user_profile


class JobListCreate(generics.ListCreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        own_param = self.request.query_params.get('own', None)
        others_param = self.request.query_params.get('others', None)
        category_param = self.request.query_params.get('category', None)

        queryset = Job.objects.all()

        if own_param is not None:
            queryset = queryset.filter(posted_by=user)
        elif others_param is not None:
            queryset = queryset.exclude(posted_by=user)

        if category_param is not None:
            queryset = queryset.filter(category=category_param)

        return queryset

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)

class JobDelete(generics.DestroyAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Job.objects.filter(posted_by=self.request.user)


class JobListCreate(generics.ListCreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        own_param = self.request.query_params.get('own', None)
        others_param = self.request.query_params.get('others', None)

        if own_param is not None:
            return Job.objects.filter(posted_by=user)
        elif others_param is not None:
            return Job.objects.exclude(posted_by=user)
        return Job.objects.all()

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)

class YourJobsList(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Job.objects.filter(posted_by=self.request.user)

class OtherJobsList(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Job.objects.exclude(posted_by=self.request.user)

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)

    @action(detail=True, methods=['post'])
    def perform_job(self, request, pk=None):
        job = self.get_object()
        suggested_price = request.data.get('suggested_price')
        application, created = JobApplication.objects.get_or_create(job=job, applicant=request.user,
                                                                    suggested_price=suggested_price)
        if created:
            return Response({'status': 'Job application created!'})
        return Response({'status': 'Job application already exists!'})

class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return JobApplication.objects.filter(job__posted_by=user) | JobApplication.objects.filter(applicant=user)

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)

    def perform_update(self, serializer):
        if self.request.user != serializer.instance.job.posted_by:
            return Response({"detail": "Not authorized to accept/deny this application."}, status=status.HTTP_403_FORBIDDEN)
        super().perform_update(serializer)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        application = self.get_object()
        if request.user != application.job.posted_by:
            return Response({"detail": "Not authorized to accept this application."}, status=status.HTTP_403_FORBIDDEN)
        application.status = 'accepted'
        application.save()
        return Response({'status': 'Application accepted', 'phone_number': application.applicant.userprofile.phone_number})

    @action(detail=True, methods=['post'])
    def deny(self, request, pk=None):
        application = self.get_object()
        if request.user != application.job.posted_by:
            return Response({"detail": "Not authorized to deny this application."}, status=status.HTTP_403_FORBIDDEN)
        application.status = 'denied'
        application.save()
        return Response({'status': 'Application denied'})

class ChatRoomViewSet(viewsets.ModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        chat_room = self.get_object()
        messages = Message.objects.filter(chat_room=chat_room)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        chat_room = self.get_object()
        message = Message.objects.create(
            chat_room=chat_room,
            sender=request.user,
            content=request.data.get('content')
        )
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class ChatRoomMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        messages = Message.objects.filter(chat_room_id=pk)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class MessageListCreate(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chat_room_id = self.kwargs['chat_room_id']
        return Message.objects.filter(chat_room_id=chat_room_id)

    def perform_create(self, serializer):
        chat_room = ChatRoom.objects.get(pk=self.kwargs['chat_room_id'])
        serializer.save(sender=self.request.user, chat_room=chat_room)

class CommentListCreate(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        job_id = self.kwargs['job_id']
        return Comment.objects.filter(job_id=job_id)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class CommentDelete(generics.DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user)