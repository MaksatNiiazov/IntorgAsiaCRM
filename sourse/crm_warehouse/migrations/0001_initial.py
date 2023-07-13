# Generated by Django 4.2.1 on 2023-07-13 10:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("crm_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmployerProduct",
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
                ("product_count", models.IntegerField(default=0)),
                ("service_count", models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="SetOfServices",
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
                ("name", models.CharField(max_length=50)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="crm_app.order"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ServiceInSet",
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
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="crm_app.service",
                    ),
                ),
                (
                    "set",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="services",
                        to="crm_warehouse.setofservices",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProductService",
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
                (
                    "employer_product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="product_service",
                        to="crm_warehouse.employerproduct",
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="product_service",
                        to="crm_app.service",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Product",
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
                ("barcode", models.CharField(max_length=50)),
                ("article", models.CharField(max_length=50)),
                ("name", models.CharField(max_length=50, null=True)),
                ("count", models.IntegerField(blank=True, default=0, null=True)),
                ("declared_quantity", models.IntegerField(default=0, null=True)),
                ("actual_quantity", models.IntegerField(default=0, null=True)),
                ("size", models.CharField(blank=True, max_length=30, null=True)),
                ("color", models.CharField(blank=True, max_length=30, null=True)),
                (
                    "composition",
                    models.CharField(blank=True, max_length=150, null=True),
                ),
                ("brand", models.CharField(blank=True, max_length=90, null=True)),
                ("defective", models.IntegerField(blank=True, null=True)),
                ("good_quality", models.IntegerField(blank=True, null=True)),
                ("country", models.CharField(blank=True, max_length=50, null=True)),
                ("comment", models.TextField(blank=True, null=True)),
                ("confirmation", models.BooleanField(default=False)),
                ("defective_check", models.BooleanField(default=False)),
                ("in_work", models.BooleanField(default=False)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="products",
                        to="crm_app.order",
                    ),
                ),
            ],
        ),
    ]
