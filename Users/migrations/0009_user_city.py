# Generated by Django 4.2.6 on 2023-11-24 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0008_alter_user_avatar_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='city',
            field=models.CharField(default='', max_length=255),
        ),
    ]
