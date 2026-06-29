from io import BytesIO
from random import choice
from uuid import uuid4

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from team_finder.constants import AVATAR_COLORS, AVATAR_FONT_SIZE
from team_finder.constants import AVATAR_SIZE, AVATAR_VERTICAL_SHIFT


TEXT_COLOR = "white"


def make_initial_avatar(name: str) -> tuple[str, ContentFile]:
    """Создать PNG-аватар с первой буквой имени пользователя."""
    initial = (name or "U").strip()[:1].upper() or "U"
    background = choice(AVATAR_COLORS)

    image = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), background)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=AVATAR_FONT_SIZE)
    bbox = draw.textbbox((0, 0), initial, font=font)
    x = (AVATAR_SIZE - (bbox[2] - bbox[0])) / 2
    y = (AVATAR_SIZE - (bbox[3] - bbox[1])) / 2 - AVATAR_VERTICAL_SHIFT
    draw.text((x, y), initial, fill=TEXT_COLOR, font=font)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    filename = f"avatars/{uuid4().hex}.png"
    return filename, ContentFile(buffer.getvalue())
