# Generated by Django 5.0.4 on 2024-04-29 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manage_circles', '0007_alter_session_day_of_week_alter_session_end_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='cover',
            field=models.ImageField(null=True, upload_to='images', verbose_name='Viršelis'),
        ),
    ]