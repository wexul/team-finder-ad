from io import BytesIO
from uuid import uuid4

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont


def make_initial_avatar(name: str) -> tuple[str, ContentFile]:
    """Create a small PNG avatar with the user's first initial."""
    initial = (name or "U").strip()[:1].upper() or "U"
    colors = ["#6B7280", "#4B5563", "#2563EB", "#047857", "#7C3AED", "#B45309"]
    background = colors[ord(initial) % len(colors)]

    image = Image.new("RGB", (256, 256), background)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=120)
    bbox = draw.textbbox((0, 0), initial, font=font)
    x = (256 - (bbox[2] - bbox[0])) / 2
    y = (256 - (bbox[3] - bbox[1])) / 2 - 8
    draw.text((x, y), initial, fill="white", font=font)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    filename = f"avatars/{uuid4().hex}.png"
    return filename, ContentFile(buffer.getvalue())
