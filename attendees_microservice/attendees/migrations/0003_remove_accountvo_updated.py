# Generated by Django 4.0.3 on 2022-07-14 22:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendees', '0002_accountvo_remove_attendee_email_remove_attendee_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accountvo',
            name='updated',
        ),
    ]
