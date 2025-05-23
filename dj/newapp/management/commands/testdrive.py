from newapp.models import Task , User , Tag
from django.core.management.base import BaseCommand
import random

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        from newapp.models import User
        print(User.objects.filter(email="user@example.com").exists())

        user = User.objects.get(email="sannya@example.com")
        print(user.is_active)  # Должно быть True
        print(user.check_password('123'))
        user.set_password('password123')  # Установите правильный пароль
        user.save()
        print(user.check_password('password123'))
        tag_name = "Работа"


        u = User.objects.get(email="user@example.com")
        tag = Tag.objects.get(name=tag_name)

        names = Task.objects.filter(user_id=23)
        for i in names:
            print(i.title)
        task = Task.objects.get(id=154)
        Tags = task.tags.all()
        for i in Tags:
            print(i.name,i.id)

        tag = Tag.objects.get(name="Личное")
        tasks = Task.objects.filter(tags=tag, user_id=40)



        if tasks.exists():
            print(f"Задачи с тегом '{tag_name}':")
            for task in tasks:

                print(f"- {task.title} (ID: {task.id})")
        else:
             print(f" Нет задач с тегом '{tag_name}'")








        ''' 
        task_ids = list(range(84, 144))  # Задачи с ID от 84 до 143
        tag_ids = list(range(6, 11))  # Теги с ID от 6 до 10

        # Присваиваем тег каждой задаче (случайным образом)
        import random

        for task_id in task_ids:
            try:
                # Получаем задачу по ID
                task = Task.objects.get(id=task_id)

                # Выбираем случайный тег
                tag_id = random.choice(tag_ids)
                tag = Tag.objects.get(id=tag_id)

                # Добавляем тег к задаче
                task.tags.add(tag)
                task.save()

                print(f" Добавлен тег '{tag.name}' к задаче с ID {task_id}")
            except Task.DoesNotExist:
                print(f" Задача с ID {task_id} не найдена")
            except Tag.DoesNotExist:
                print(f" Тег с ID {tag_id} не найден")
        '''



