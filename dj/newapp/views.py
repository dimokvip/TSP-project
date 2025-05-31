from rest_framework import viewsets
from .models import User, Task, Tag
from .serializers import UserSerializer, TaskSerializer, TagSerializer,ChangePasswordSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .permissions import IsOwnerOrAdmin, IsTaskOwnerOrAdmin, IsTagOwnerOrAdmin
from rest_framework.decorators import action
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer
from .models import Task
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterForm, TaskForm
from .models import Task
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import *
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.http import JsonResponse
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Task
from .serializers import TaskSerializer, UserSerializer
def home(request):
    return render(request, 'home.html')

@login_required
def profile_view(request):
    tasks = Task.objects.filter(user=request.user).prefetch_related('tags')
    return render(request, 'profile.html', {'tasks': tasks})



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_api(request):
    user = request.user
    tasks = Task.objects.filter(user=user).prefetch_related('tags')
    # Фильтрация по тегам
    tags = Tag.objects.filter(tasks__user=user).distinct()
    if tags:
        tag_ids = [int(t) for t in tags.split(',') if t.isdigit()]
        tasks = tasks.filter(tags__in=tag_ids).distinct()

    # Фильтрация по приоритету
    priority = request.query_params.get('priority')
    if priority in ['low', 'medium', 'high']:
        tasks = tasks.filter(priority=priority)

    # Сортировка
    ordering = request.query_params.get('ordering')
    allowed_ordering = ['created_at', '-created_at', 'deadline', '-deadline']
    if ordering in allowed_ordering:
        tasks = tasks.order_by(ordering)
    else:
        tasks = tasks.order_by('-created_at')  # default сортировка

    tasks_serializer = TaskSerializer(tasks, many=True)
    user_data = UserSerializer(user).data
    return Response({'user': user_data, 'tasks': tasks_serializer.data})
    tasks_data = TaskSerializer(tasks, many=True).data
    user_data = UserSerializer(user).data
    return Response({
        'user': user_data,
        'tasks': tasks_data,
        'tags': TagSerializer(tags, many=True).data
    })

def profile_page(request):
    return render(request, 'profile.html')
def session_login(request):
    # Аутентификация через JWT
    jwt_auth = JWTAuthentication()
    user_auth_tuple = jwt_auth.authenticate(request)
    if user_auth_tuple is None:
        return Response({'detail': 'Invalid token'}, status=401)
    user, validated_token = user_auth_tuple

    # Логиним пользователя в сессию Django
    login(request, user)
    return Response({'detail': 'Logged in to session'})

def register_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Некорректные данные'}, status=400)

        form = RegisterForm(data)
        if form.is_valid():
            user = form.save()
            print(f"Пользователь {user.email} создан")  # ✅ Убедись, что это сообщение появляется
            return JsonResponse({'success': True})
        else:
            print("Ошибки формы:", form.errors)  # ✅ Добавь лог
            return JsonResponse(form.errors, status=400)

    return JsonResponse({'error': 'Только POST запросы'}, status=405)

def register_page(request):
    return render(request, 'register.html')
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
def logout_html_view(request):
    # Просто отдать страницу, которая очистит localStorage и переадресует
    return render(request, 'logout.html')
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task_api(request):
    serializer = TaskSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
def create_task_page(request):
    return render(request, 'create-task.html')
def create_task_view(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            form.save_m2m()  # для tags
            return redirect('profile')
    else:
        form = TaskForm()
    return render(request, 'create-task.html', {'form': form})
def login_page(request):
    return render(request, 'login.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('profile')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})



@login_required
def dashboard_view(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'tasks': tasks})

def logout_view(request):
    logout(request)
    return redirect('login')

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated, IsTagOwnerOrAdmin]

    @action(detail=False, methods=['get'], url_path='user-tags')
    def user_tags(self, request):
        # Получаем текущего пользователя
        user = request.user

        # Находим все теги, связанные с задачами этого пользователя
        tags = Tag.objects.filter(tasks__user=user).distinct()
        serializer = self.get_serializer(tags, many=True)
        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskOwnerOrAdmin]

    @action(detail=False, methods=['get'], url_path='user-tasks')
    def user_tasks(self, request):
        # Получаем текущего пользователя
        user = request.user

        # Фильтруем задачи по пользователю
        tasks = Task.objects.filter(user=user)

        # Сериализуем задачи
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='user-tasks-by-tag')
    def user_tasks_by_tag(self, request):
        # Получаем текущего пользователя и тег из параметров запроса
        user = request.user
        tag_name = request.query_params.get('tag')

        # Если тег не указан, возвращаем ошибку
        if not tag_name:
            return Response({'error': 'Тег не указан'}, status=400)

        try:
            # Получаем объект тега
            tag = Tag.objects.get(name=tag_name)
        except Tag.DoesNotExist:
            return Response({'error': 'Тег не найден'}, status=404)

        # Фильтруем задачи по пользователю и тегу
        tasks = Task.objects.filter(user=user, tags=tag)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({'message': 'Пароль успешно изменён'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data['refresh'])
            token.blacklist()
            return Response({'message': 'Успешный выход'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'message': 'Доступ разрешен'}, status=status.HTTP_200_OK)
