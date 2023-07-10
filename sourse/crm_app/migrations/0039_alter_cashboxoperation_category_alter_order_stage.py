# Generated by Django 4.2.1 on 2023-07-09 15:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("crm_app", "0038_service_acceptance"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cashboxoperation",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="crm_app.cashboxcategory",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="stage",
            field=models.CharField(
                choices=[
                    ("acceptance", "Приемка"),
                    ("database_loading", "Загрузка в базу"),
                    ("unpacking", "Распаковка"),
                    ("quality_check", "Выдача ОТК"),
                    ("invoice_generation", "Выставка счета"),
                    ("dispatch", "Отправка"),
                    ("dispatched", "Оправленно"),
                ],
                default="database_loading",
                max_length=20,
            ),
        ),
    ]