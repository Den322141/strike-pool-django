import club.uploads
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0004_initial_catalog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='photo',
            field=models.ImageField(blank=True, upload_to='menu/', validators=[club.uploads.validate_photo], verbose_name='Фото'),
        ),
    ]
