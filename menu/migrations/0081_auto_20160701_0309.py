# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-07-01 03:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import menu.models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0080_auto_20160629_0250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ofrece',
            name='precio',
            field=models.FloatField(validators=[menu.models.validate_monto]),
        ),
        migrations.AlterField(
            model_name='pedido',
            name='precio',
            field=models.FloatField(validators=[menu.models.validate_monto]),
        ),
        migrations.AlterField(
            model_name='plato',
            name='precio',
            field=models.FloatField(validators=[menu.models.validate_monto]),
        ),
        migrations.AlterField(
            model_name='plato_en_menu',
            name='menu',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='menu.MENU'),
        ),
        migrations.AlterField(
            model_name='puntuacion',
            name='comentario',
            field=models.CharField(default='', max_length=300),
        ),
    ]