from django.test import TestCase
from django.urls import reverse

from team_finder.constants import PROJECT_STATUS_CLOSED

from projects.models import Project, Skill
from users.models import User


class ProjectFlowTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com", password="pass12345", name="Олег", surname="Автор"
        )
        self.member = User.objects.create_user(
            email="member@example.com", password="pass12345", name="Мила", surname="Участник"
        )
        self.project = Project.objects.create(
            owner=self.owner,
            name="Django Hub",
            description="Test project",
        )
        self.project.participants.add(self.owner)

    def test_project_list_available_for_guest(self):
        response = self.client.get(reverse("projects:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django Hub")

    def test_owner_can_create_project(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("projects:create"),
            {
                "name": "New API",
                "description": "API",
                "github_url": "https://github.com/example/api",
                "status": "open",
            },
        )
        created = Project.objects.get(name="New API")
        self.assertRedirects(response, reverse("projects:detail", args=[created.pk]))
        self.assertTrue(created.participants.filter(pk=self.owner.pk).exists())

    def test_member_can_toggle_participation(self):
        self.client.force_login(self.member)
        response = self.client.post(reverse("projects:toggle_participate", args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.project.participants.filter(pk=self.member.pk).exists())

    def test_owner_can_complete_project(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("projects:complete", args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, PROJECT_STATUS_CLOSED)

    def test_skill_filtering(self):
        skill = Skill.objects.create(name="Django")
        self.project.skills.add(skill)
        response = self.client.get(reverse("projects:list"), {"skill": "Django"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django Hub")

    def test_owner_can_add_skill_by_name(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("projects:add_skill", args=[self.project.pk]),
            {"name": "Docker"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.project.skills.filter(name="Docker").exists())

    def test_foreign_user_cannot_add_skill(self):
        self.client.force_login(self.member)
        response = self.client.post(
            reverse("projects:add_skill", args=[self.project.pk]),
            {"name": "Docker"},
        )
        self.assertEqual(response.status_code, 403)
