# Generated by Django 4.2.1 on 2023-06-11 08:46

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_alter_user_joined_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="joined_date",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
