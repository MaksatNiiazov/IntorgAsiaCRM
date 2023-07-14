# Generated by Django 4.2.1 on 2023-07-14 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("crm_app", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="amount_paid",
            field=models.IntegerField(default=0),
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
                    ("closed", "Закрыт"),
                ],
                default="database_loading",
                max_length=20,
            ),
        ),
    ]
