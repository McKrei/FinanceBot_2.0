# Generated by Django 4.2 on 2023-05-20 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0004_alter_category_name_alter_subcategory_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='limitinmonth',
            name='month',
            field=models.CharField(max_length=64, verbose_name='Месяц в формате MM.YYYY'),
        ),
        migrations.AlterField(
            model_name='limitstartmonth',
            name='month',
            field=models.CharField(max_length=64, verbose_name='Месяц в формате MM.YYYY'),
        ),
        migrations.AlterField(
            model_name='subcategoryreduction',
            name='reduction',
            field=models.CharField(max_length=64, verbose_name='Сокращение категории'),
        ),
    ]
