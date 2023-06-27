# Generated by Django 4.2.1 on 2023-06-15 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("crm_warehouse", "0006_alter_product_count"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="actual_quantity",
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="brand",
            field=models.CharField(blank=True, max_length=90, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="comment",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="composition",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="country",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="declared_quantity",
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="ghest_circumference",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="girth_waist",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="height",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="length",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="name",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="width",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
