# Generated by Django 4.2.7 on 2023-11-07 15:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("djstore", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="products",
            name="description",
            field=models.TextField(null=True),
        ),
    ]
