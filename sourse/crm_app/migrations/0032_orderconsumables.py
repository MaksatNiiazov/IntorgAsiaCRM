# Generated by Django 4.2.1 on 2023-07-06 07:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("crm_app", "0031_alter_service_options_alter_cashboxoperation_comment"),
    ]

    operations = [
        migrations.CreateModel(
            name="OrderConsumables",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("count", models.IntegerField(default=0)),
                ("cost_price", models.IntegerField(default=0)),
                ("price", models.IntegerField(default=0)),
                (
                    "consumable",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="crm_app.consumables",
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="crm_app.order"
                    ),
                ),
            ],
        ),
    ]
