from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenVerifyView
)
from . import views
from newapp.views import profile_api

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
#router.register(r'tasks', views.TaskViewSet)
router.register(r'tags', views.TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('logout/', views.LogoutView.as_view(), name='logout_api'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('register/', views.register_view, name='register'),
    path('profile/', profile_api, name='profile-api'),
    path('tasks/create/', views.create_task_api, name='create_task_api'),
]