from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('text', models.TextField()),
                ('date', models.DateField()),
                ('rating', models.PositiveSmallIntegerField(default=5)),
            ],
        ),
        migrations.AddField(
            model_name='gametype',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='gametype',
            name='image',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='gametype',
            name='label',
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name='gametype',
            name='slug',
            field=models.SlugField(blank=True),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='image',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='portion',
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name='zone',
            name='vip',
            field=models.BooleanField(default=False),
        ),
    ]
