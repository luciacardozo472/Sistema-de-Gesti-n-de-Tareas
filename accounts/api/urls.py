from django.urls import path
from .views import RegisterView, UserListView, CurrentUserView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/me/', CurrentUserView.as_view(), name='user-me'),
]