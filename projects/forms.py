from django import forms
from django.core.exceptions import ValidationError

from users.forms import validate_github_url

from .models import PROJECT_STATUS_CHOICES, Project


class ProjectForm(forms.ModelForm):
    status = forms.ChoiceField(label="Статус", choices=PROJECT_STATUS_CHOICES)

    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
        }

    def clean_name(self):
        name = " ".join(self.cleaned_data["name"].strip().split())
        if not name:
            raise ValidationError("Название проекта обязательно")
        return name

    def clean_github_url(self):
        return validate_github_url(self.cleaned_data.get("github_url", ""))
