# Generated by Django 4.2.3 on 2023-08-14 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("trakit", "0003_remove_task_duedate_remove_task_priority"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="description",
            field=models.TextField(blank=True),
        ),
    ]