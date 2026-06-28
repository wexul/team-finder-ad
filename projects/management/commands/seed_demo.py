from django.core.management.base import BaseCommand

from projects.models import Project, Skill
from users.models import User


class Command(BaseCommand):
    help = "Create demo users, skills and projects for TeamFinder."

    def handle(self, *args, **options):
        users = [
            ("maria@example.com", "Мария", "Соколова"),
            ("ivan@example.com", "Иван", "Петров"),
            ("anna@example.com", "Анна", "Ким"),
        ]
        created_users = []
        for email, name, surname in users:
            user, created = User.objects.get_or_create(email=email, defaults={"name": name, "surname": surname})
            if created:
                user.set_password("password")
                user.save()
            created_users.append(user)

        skills = {name: Skill.objects.get_or_create(name=name)[0] for name in ["Django", "PostgreSQL", "Docker", "Frontend", "API"]}

        for owner, project_name, skill_names in [
            (created_users[0], "Платформа обмена pet-проектами", ["Django", "PostgreSQL"]),
            (created_users[1], "API для трекера привычек", ["API", "Docker"]),
            (created_users[2], "Мини-сервис портфолио", ["Frontend", "Django"]),
        ]:
            project, _ = Project.objects.get_or_create(
                owner=owner,
                name=project_name,
                defaults={"description": "Демо-проект для проверки интерфейса TeamFinder."},
            )
            project.participants.add(owner)
            project.skills.set([skills[name] for name in skill_names])

        self.stdout.write(self.style.SUCCESS("Demo data created. Login: maria@example.com / password"))
