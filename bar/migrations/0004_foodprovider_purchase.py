# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-30 13:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bookkeeper', '0002_auto_20160330_1155'),
        ('bar', '0003_auto_20160330_1318'),
    ]

    operations = [
        migrations.CreateModel(
            name='FoodProvider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('material_account', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='supply', to='bookkeeper.Account')),
                ('monetary_account', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='cost', to='bookkeeper.Account')),
            ],
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('when', models.DateTimeField(auto_now=True)),
                ('cost', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('unit_count', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('unit_size', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bar.FoodProvider')),
                ('stuff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bar.FoodStuff')),
                ('transactions', models.ManyToManyField(to='bookkeeper.Transaction')),
            ],
        ),
    ]
