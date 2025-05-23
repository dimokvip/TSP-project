from rest_framework import serializers
from .models import User, Task, Tag
from django.contrib.auth import get_user_model

User = get_user_model()

# Сериализатор для пользователя
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # Хеширование пароля
        user.save()
        return user

# Сериализатор для тега
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

# Сериализатор для задачи
class TaskSerializer(serializers.ModelSerializer):
    # Используем PrimaryKeyRelatedField для связи многие ко многим
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'created_at', 'status', 'priority', 'deadline', 'tags', 'user']

    def create(self, validated_data):
        # Извлекаем теги из данных
        tags = validated_data.pop('tags', [])
        # Создаем задачу
        task = Task.objects.create(**validated_data)
        # Добавляем теги к задаче
        task.tags.set(tags)
        task.save()
        return task

    def update(self, instance, validated_data):
        # Извлекаем теги из данных
        tags = validated_data.pop('tags', [])
        # Обновляем данные задачи
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Если теги присутствуют, обновляем их
        if tags:
            instance.tags.set(tags)
        instance.save()
        return instance

# Сериализатор для смены пароля
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, attrs):
        user = self.context['user']
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({'old_password': 'Неверный текущий пароль'})
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({'new_password': 'Новый пароль не должен совпадать с текущим'})
        return attrs
