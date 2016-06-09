# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-04 18:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0016_auto_20160603_1316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plato',
            name='path_img',
            field=models.FileField(default=1, upload_to=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='plato_en_menu',
            name='menu',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='menu.MENU'),
        ),
    ]
