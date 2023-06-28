# Generated by Django 4.2.1 on 2023-06-28 11:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("crm_warehouse", "0021_remove_setofservices_product_setofservices_order"),
    ]

    operations = [
        migrations.AlterField(
            model_name="serviceinset",
            name="set",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="services",
                to="crm_warehouse.setofservices",
            ),
        ),
    ]
