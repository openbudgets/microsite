# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-08-29 14:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vizmanager', '0006_dataset_initial_measure'),
    ]

    operations = [
        migrations.CreateModel(
            name='Indicator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('indicator', models.CharField(max_length=200, verbose_name='indicator')),
            ],
            options={
                'verbose_name': 'Indicator',
                'verbose_name_plural': 'Indicators',
            },
        ),
        migrations.CreateModel(
            name='KPI',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'KPI',
                'verbose_name_plural': 'KPIs',
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('url', models.URLField(primary_key=True, serialize=False, verbose_name='Url')),
            ],
            options={
                'verbose_name': 'Organization',
                'verbose_name_plural': 'Organizations',
            },
        ),
        migrations.CreateModel(
            name='Phase',
            fields=[
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('url', models.URLField(primary_key=True, serialize=False, verbose_name='Url')),
            ],
            options={
                'verbose_name': 'Budget Phase',
                'verbose_name_plural': 'Budget Phases',
            },
        ),
        migrations.CreateModel(
            name='Year',
            fields=[
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('url', models.URLField(primary_key=True, serialize=False, verbose_name='Url')),
            ],
            options={
                'verbose_name': 'Year',
                'verbose_name_plural': 'Years',
            },
        ),
        migrations.AddField(
            model_name='kpi',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vizmanager.Organization'),
        ),
        migrations.AddField(
            model_name='kpi',
            name='phase',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vizmanager.Phase'),
        ),
        migrations.AddField(
            model_name='kpi',
            name='year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vizmanager.Year'),
        ),
        migrations.AddField(
            model_name='microsite',
            name='kpi_set',
            field=models.ManyToManyField(to='vizmanager.KPI'),
        ),
    ]
