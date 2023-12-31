# Generated by Django 4.2.1 on 2023-07-16 11:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("crm_warehouse", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="employerproduct",
            name="employer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="employer_product",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="employerproduct",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="employer_product",
                to="crm_warehouse.product",
            ),
        ),
    ]
