# Generated by Django 4.1.3 on 2022-12-20 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Quiz_Maker', '0006_quiz_quiz_pw'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='order',
            field=models.IntegerField(default=0, null=True),
        ),
    ]