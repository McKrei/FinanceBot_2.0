# Generated by Django 4.1.2 on 2023-05-20 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mainapp", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="name",
            field=models.CharField(max_length=32, verbose_name="Название категории"),
        ),
        migrations.AlterField(
            model_name="subcategory",
            name="name",
            field=models.CharField(max_length=32, verbose_name="Название категории"),
        ),
    ]
