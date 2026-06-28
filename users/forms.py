import re
from urllib.parse import urlparse

from django import forms
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from django.core.exceptions import ValidationError

from .models import User

PHONE_RE = re.compile(r"^(?:8|\+7)\d{10}$")


def normalize_phone(value: str) -> str:
    phone = (value or "").strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not phone:
        return ""
    if not PHONE_RE.match(phone):
        raise ValidationError("Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX")
    if phone.startswith("8"):
        phone = "+7" + phone[1:]
    return phone


def validate_github_url(value: str) -> str:
    url = (value or "").strip()
    if not url:
        return ""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValidationError("Введите корректную ссылку")
    host = parsed.netloc.lower()
    if host != "github.com" and not host.endswith(".github.com"):
        raise ValidationError("Ссылка должна вести на GitHub")
    return url


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password"]

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Пользователь с таким email уже существует")
        return email

    def save(self, commit=True):
        user = User(
            name=self.cleaned_data["name"],
            surname=self.cleaned_data["surname"],
            email=self.cleaned_data["email"],
        )
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")
        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise ValidationError("Неверный имейл или пароль")
            if not user.is_active:
                raise ValidationError("Пользователь заблокирован")
            cleaned["user"] = user
        return cleaned


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]

    def clean_phone(self):
        phone = normalize_phone(self.cleaned_data.get("phone", ""))
        if phone:
            qs = User.objects.filter(phone=phone)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Такой телефон уже используется")
        return phone

    def clean_github_url(self):
        return validate_github_url(self.cleaned_data.get("github_url", ""))


class PasswordChangeForm(DjangoPasswordChangeForm):
    def clean_new_password2(self):
        password2 = super().clean_new_password2()
        if password2:
            password_validation.validate_password(password2, self.user)
        return password2
