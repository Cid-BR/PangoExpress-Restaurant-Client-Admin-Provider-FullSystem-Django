# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-17 12:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0070_auto_20160616_1925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plato_en_menu',
            name='menu',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='menu.MENU'),
        ),
        migrations.AlterField(
            model_name='transaccion',
            name='billetera',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='menu.BILLETERA'),
        ),
    ]
