from django.test import TestCase
from django.urls import reverse

from users.forms import ProfileForm
from users.models import User


class UserFlowTests(TestCase):
    def test_register_login_by_email(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "name": "Мария",
                "surname": "Иванова",
                "email": "maria@example.com",
                "password": "pass12345",
            },
        )
        self.assertRedirects(response, reverse("projects:list"))
        self.assertTrue(User.objects.filter(email="maria@example.com").exists())

    def test_phone_normalized_and_unique(self):
        first = User.objects.create_user(
            email="first@example.com",
            password="pass",
            name="A",
            surname="B",
            phone="+79991234567",
        )
        second = User.objects.create_user(
            email="second@example.com",
            password="pass",
            name="C",
            surname="D",
        )
        form = ProfileForm(
            data={
                "name": second.name,
                "surname": second.surname,
                "about": "",
                "phone": "89991234567",
                "github_url": "",
            },
            instance=second,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)
        self.assertEqual(first.phone, "+79991234567")

    def test_github_url_must_be_github(self):
        user = User.objects.create_user(
            email="user@example.com",
            password="pass",
            name="A",
            surname="B",
        )
        form = ProfileForm(
            data={
                "name": "A",
                "surname": "B",
                "about": "",
                "phone": "+79990000000",
                "github_url": "https://notgithub.com/github.com/fake",
            },
            instance=user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("github_url", form.errors)
