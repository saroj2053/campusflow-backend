# Generated by Django 4.2.7 on 2024-02-28 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transfer_credits', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transfercredits',
            name='possibleTransferrableCredits',
            field=models.IntegerField(null=True),
        ),
    ]