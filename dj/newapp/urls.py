from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login-html/', views.login_page, name='login'),
    path('logout/', views.logout_html_view, name='logout'),
    path('register-html/', views.register_page, name='register_page'),
    path('profile/', views.profile_view, name='profile'),
    path('profile-html/', views.profile_page, name='profile_page'),
    path('create-task-html/', views.create_task_view, name='create_task'),
    path('register/', views.register_view, name='register'),
    path('create-task.html', views.create_task_page, name='create_task_page'),

]