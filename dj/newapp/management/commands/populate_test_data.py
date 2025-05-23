from django.core.management.base import BaseCommand
from newapp.models import User, Task, Tag
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()


class Command(BaseCommand):
    help = "Заполняет базу данных тестовыми задачами"

    def handle(self, *args, **kwargs):
        # Создаем теговые категории, если их нет
        tags = ['Работа', 'Дом', 'Учеба', 'Здоровье', 'Личное']
        for tag_name in tags:
            Tag.objects.get_or_create(name=tag_name)

        # Генерируем пользователей, если их нет
        if not User.objects.exists():
            for _ in range(5):  # например, 5 случайных пользователей
                email = fake.unique.email()
                password = 'password123'
                first_name = fake.first_name()
                last_name = fake.last_name()
                User.objects.create_user(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
            self.stdout.write(self.style.SUCCESS('Создано 5 случайных пользователей.'))

        # Получаем всех пользователей
        users = User.objects.all()

        # Получаем все теги
        tag_objs = list(Tag.objects.all())

        statuses = ['todo', 'in_progress', 'done']
        priorities = ['low', 'medium', 'high']

        # Создаем задачи
        for _ in range(60):
            user = random.choice(users)
            created_at = fake.date_time_between(start_date='-30d', end_date='now')
            deadline = created_at + timedelta(days=random.randint(1, 14))

            task = Task.objects.create(
                user=user,
                title=fake.sentence(nb_words=4),
                description=fake.text(max_nb_chars=200),
                created_at=created_at,
                status=random.choice(statuses),
                priority=random.choice(priorities),
                tag=random.choice(tag_objs),
                deadline=deadline if random.choice([True, False]) else None
            )

        self.stdout.write(self.style.SUCCESS(' Успешно создано 60 тестовых задач!'))
