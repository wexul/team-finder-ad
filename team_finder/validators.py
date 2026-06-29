"""Reusable validators and normalizers."""

import re
from urllib.parse import urlparse

from django.core.exceptions import ValidationError

PHONE_RE = re.compile(r"^(?:8|\+7)\d{10}$")


def normalize_spaces(value: str) -> str:
    return " ".join((value or "").strip().split())


def normalize_phone(value: str) -> str:
    phone = (
        (value or "")
        .strip()
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )
    if not phone:
        return ""
    if not PHONE_RE.match(phone):
        raise ValidationError(
            "Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
        )
    if phone.startswith("8"):
        return "+7" + phone[1:]
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
