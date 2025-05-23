from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, TaskViewSet, TagViewSet, ProtectedView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import RegisterView, ChangePasswordView, LogoutView
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('protected/', ProtectedView.as_view(), name='protected'),
]