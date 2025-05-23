from rest_framework import viewsets
from .models import User, Task, Tag
from .serializers import UserSerializer, TaskSerializer, TagSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .permissions import IsOwnerOrAdmin, IsTaskOwnerOrAdmin, IsTagOwnerOrAdmin
from rest_framework.decorators import action



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
