# Generated by Django 3.2.18 on 2023-05-04 11:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredient',
            old_name='measure_unit',
            new_name='measurement_unit',
        ),
    ]
