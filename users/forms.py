from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError

from team_finder.validators import normalize_phone, validate_github_url

from .models import User


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password"]


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
            users = User.objects.filter(phone=phone)
            if self.instance.pk:
                users = users.exclude(pk=self.instance.pk)
            if users.exists():
                raise ValidationError("Такой телефон уже используется")
        return phone

    def clean_github_url(self):
        return validate_github_url(
            self.cleaned_data.get("github_url", "")
        )
