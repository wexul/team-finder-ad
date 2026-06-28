from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models import Q

from .managers import UserManager
from .utils import make_initial_avatar

NAME_MAX_LENGTH = 124
PHONE_MAX_LENGTH = 12
ABOUT_MAX_LENGTH = 256


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("email", unique=True)
    name = models.CharField("имя", max_length=NAME_MAX_LENGTH)
    surname = models.CharField("фамилия", max_length=NAME_MAX_LENGTH)
    avatar = models.ImageField("аватар", upload_to="avatars/", blank=True)
    phone = models.CharField("телефон", max_length=PHONE_MAX_LENGTH, blank=True, default="")
    github_url = models.URLField("GitHub", blank=True)
    about = models.TextField("о себе", max_length=ABOUT_MAX_LENGTH, blank=True)
    date_joined = models.DateTimeField("дата регистрации", auto_now_add=True)
    is_active = models.BooleanField("активен", default=True)
    is_staff = models.BooleanField("администратор", default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["phone"],
                condition=~Q(phone=""),
                name="unique_non_empty_user_phone",
            )
        ]

    def save(self, *args, **kwargs):
        if not self.avatar and self.name:
            filename, content = make_initial_avatar(self.name)
            self.avatar.save(filename, content, save=False)
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.name} {self.surname}".strip()

    def __str__(self):
        return f"{self.full_name} <{self.email}>"
