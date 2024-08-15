from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import (
    JobViewSet,
    UserProfileViewSet,
    JobApplicationViewSet,
    MessageListCreate, ChatRoomViewSet, CommentListCreate, CommentDelete
)

router = DefaultRouter()
router.register(r'jobs', JobViewSet)
router.register(r'profiles', UserProfileViewSet)
router.register(r'applications', JobApplicationViewSet)
router.register(r'chat_rooms', ChatRoomViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('jobs/', JobViewSet.as_view({'get': 'list', 'post': 'create'}), name='job-list-create'),
    path('your-jobs/', JobViewSet.as_view({'get': 'list'}), name='your-jobs'),
    path('other-jobs/', JobViewSet.as_view({'get': 'list'}), name='other-jobs'),
    path('jobs/delete/<int:pk>/', JobViewSet.as_view({'delete': 'destroy'}), name='job-delete'),
    path('profile/', UserProfileViewSet.as_view({'get': 'me', 'put': 'me'}), name='user-profile-retr-upd'),
    path('chat_rooms/<int:chat_room_id>/messages/', MessageListCreate.as_view(), name='chat-room-messages'),
    path('jobs/<int:job_id>/comments/', views.CommentListCreate.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', views.CommentDelete.as_view(), name='comment-delete'),
]
