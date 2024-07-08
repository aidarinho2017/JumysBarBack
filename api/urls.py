from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import (
    JobViewSet,
    UserProfileViewSet,
    JobApplicationViewSet,
    YourJobsList,
    OtherJobsList,
    JobListCreate,
    JobDelete,
    UserProfileRetrieveUpdate,
)

router = DefaultRouter()
router.register(r'jobs', JobViewSet)
router.register(r'profiles', UserProfileViewSet)
router.register(r'applications', JobApplicationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('jobs/', views.JobListCreate.as_view(), name='job-list-create'),
    path('your-jobs/', views.YourJobsList.as_view(), name='your-jobs'),
    path('other-jobs/', views.OtherJobsList.as_view(), name='other-jobs'),
    path('jobs/delete/<int:pk>/', views.JobDelete.as_view(), name='job-delete'),
    path('profile/', views.UserProfileRetrieveUpdate.as_view(), name='user-profile-retrieve-update'),
]
