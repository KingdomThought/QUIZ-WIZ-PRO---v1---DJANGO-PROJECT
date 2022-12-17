# Generated by Django 4.1.3 on 2022-12-17 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Login', '0002_remove_studenttype_user_studenttype_user_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_type', models.CharField(max_length=50)),
                ('user_id', models.IntegerField(default=0)),
            ],
        ),
        migrations.DeleteModel(
            name='StudentType',
        ),
    ]
