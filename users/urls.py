from django.urls import path

from .views import UserDetailView, UserListView, UserProfileView

app_name = "users"

urlpatterns = [
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("", UserListView.as_view(), name="user-list"),
    path("<int:pk>/", UserDetailView.as_view(), name="user-detail"),
]
