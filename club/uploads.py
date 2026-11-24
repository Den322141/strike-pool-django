from pathlib import Path
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError


def validate_photo(value):
    if value.size > 5 * 1024 * 1024:
        raise ValidationError("Выберите изображение размером до 5 МБ.")
    suffixes = Path(value.name).suffixes
    formats = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".webp": "WEBP"}
    if len(suffixes) != 1 or suffixes[0].lower() not in formats:
        raise ValidationError("Используйте одно расширение JPEG, PNG или WebP.")
    try:
        value.seek(0)
        with Image.open(value) as picture:
            if picture.format != formats[suffixes[0].lower()]:
                raise ValidationError("Содержимое изображения не соответствует расширению.")
            picture.verify()
    except (OSError, ValueError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
        raise ValidationError("Не удалось прочитать изображение.") from exc
    finally:
        value.seek(0)
