# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-11 13:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('answerer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionVectorized',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=500)),
                ('answer', models.CharField(max_length=500)),
            ],
        ),
    ]
