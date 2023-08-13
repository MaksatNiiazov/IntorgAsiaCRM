# Generated by Django 4.2.1 on 2023-08-13 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm_app', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='actual_shipment_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='date_of_actual_arrival',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cashbox',
            name='balance',
            field=models.IntegerField(default=0),
        ),
    ]
