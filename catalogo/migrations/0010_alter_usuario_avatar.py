# Generated by Django 5.1.7 on 2025-04-01 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0009_usuario_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='avatar',
            field=models.ImageField(blank=True, default='perfiles/default.png', null=True, upload_to='avatars/'),
        ),
    ]
