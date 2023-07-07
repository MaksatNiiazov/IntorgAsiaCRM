# Generated by Django 4.2.1 on 2023-07-05 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0013_alter_user_username"),
    ]

    operations = [
        migrations.RemoveField(model_name="user", name="phone_number",),
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(
                blank=True,
                help_text="Номер телефона",
                max_length=100,
                null=True,
                unique=True,
            ),
        ),
    ]