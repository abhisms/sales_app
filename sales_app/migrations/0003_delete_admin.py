# Generated by Django 5.0.7 on 2025-03-03 19:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales_app', '0002_rename_adminuser_admin'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Admin',
        ),
    ]
