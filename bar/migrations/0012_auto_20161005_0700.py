# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-10-05 07:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bar', '0011_auto_20161005_0639'),
    ]

    operations = [
        migrations.AddField(
            model_name='saleoffer',
            name='cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AlterField(
            model_name='calculation',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calculations', to='bar.RecipeIngredient'),
        ),
        migrations.AlterField(
            model_name='calculation',
            name='sale_offer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calculations', to='bar.SaleOffer'),
        ),
    ]
