# Generated by Django 4.0.3 on 2022-07-15 00:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendees', '0004_accountvo_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendee',
            name='email',
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='attendee',
            name='name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='accountvo',
            name='email',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]