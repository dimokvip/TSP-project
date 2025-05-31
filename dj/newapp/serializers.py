from rest_framework import serializers
from .models import User, Task, Tag
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
        user.set_password(password)  # хеширование
        user.save()
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email  # добавление произвольных данных
        return token


# Сериализатор для тега
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

# Сериализатор для задачи
class TaskSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)

    new_tags = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text="Новые теги по именам"
    )
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'created_at', 'status', 'priority', 'deadline', 'tags', 'new_tags', 'user']

    def create(self, validated_data):
        new_tags = validated_data.pop('new_tags', [])
        tags = validated_data.pop('tags', [])

        # Создаем задачу без тегов
        task = Task.objects.create(**validated_data)

        # Сначала добавляем существующие теги
        if tags:
            task.tags.set(tags)

        # Создаем и добавляем новые теги
        for tag_name in new_tags:
            tag_obj, created = Tag.objects.get_or_create(name=tag_name)
            task.tags.add(tag_obj)

        task.save()
        return task

    def update(self, instance, validated_data):
        new_tags = validated_data.pop('new_tags', [])
        tags = validated_data.pop('tags', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if tags:
            instance.tags.set(tags)

        for tag_name in new_tags:
            tag_obj, created = Tag.objects.get_or_create(name=tag_name)
            instance.tags.add(tag_obj)

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
