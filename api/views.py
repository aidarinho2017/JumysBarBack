from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from .models import Job, UserProfile, JobApplication
from .serializers import JobSerializer, UserSerializer, UserProfileSerializer, JobApplicationSerializer


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get', 'post', 'put'])
    def my_profile(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        if request.method in ['POST', 'PUT']:
            serializer = self.get_serializer(profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
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
        if self.action == 'list':
            # If filtering for own jobs
            if 'own' in self.request.query_params:
                return Job.objects.filter(posted_by=user)
            # If filtering for jobs posted by others
            elif 'others' in self.request.query_params:
                return Job.objects.exclude(posted_by=user)
        return Job.objects.all()

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
        application, created = JobApplication.objects.get_or_create(job=job, applicant=request.user)
        if created:
            return Response({'status': 'Application submitted'})
        else:
            return Response({'status': 'Application already exists'}, status=400)

class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]

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

