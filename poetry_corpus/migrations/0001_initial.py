# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-10 23:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Poem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст')),
                ('name', models.CharField(blank=True, max_length=50, verbose_name='Нвзвание стихотворения')),
                ('author', models.CharField(max_length=50, verbose_name='Автор')),
                ('date_from', models.IntegerField(blank=True, null=True, verbose_name='Дата написания - первый год')),
                ('date_to', models.IntegerField(blank=True, null=True, verbose_name='Дата написания - второй год')),
            ],
            options={
                'verbose_name_plural': 'Стихотворения',
                'verbose_name': 'Стихотворение',
            },
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('theme', models.CharField(max_length=50, verbose_name='Тема')),
            ],
        ),
        migrations.AddField(
            model_name='poem',
            name='themes',
            field=models.ManyToManyField(blank=True, related_name='poems', to='poetry_corpus.Theme', verbose_name='Темы'),
        ),
    ]