# Generated by Django 4.2.1 on 2023-06-22 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("crm_app", "0017_orderservice_date_orderservice_employer_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderservice",
            name="confirmed",
            field=models.BooleanField(default=False),
        ),
    ]
