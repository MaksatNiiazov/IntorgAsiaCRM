# Generated by Django 4.2.1 on 2023-06-22 06:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("crm_app", "0016_order_good_quality"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderservice",
            name="date",
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name="orderservice",
            name="employer",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="orderservice",
            name="salary",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="orderservice",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="crm_app.order"
            ),
        ),
        migrations.DeleteModel(name="EmployerService",),
    ]
