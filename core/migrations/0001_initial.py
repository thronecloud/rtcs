# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import geoposition.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CabRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('origin', geoposition.fields.GeopositionField(max_length=42)),
                ('destination', geoposition.fields.GeopositionField(max_length=42)),
                ('moment', models.DateTimeField(default=django.utils.timezone.now)),
                ('gender', models.IntegerField(default=999, choices=[(1, b'Female'), (2, b'Male'), (999, b'Indiferent')])),
                ('origin_name', models.CharField(max_length=255, null=True, blank=True)),
                ('destination_name', models.CharField(max_length=255, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='DirectionsRoute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('duration', models.IntegerField(default=0)),
                ('cabrequest', models.ForeignKey(related_name='routes', to='core.CabRequest')),
            ],
        ),
        migrations.CreateModel(
            name='DirectionsStep',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField()),
                ('start', geoposition.fields.GeopositionField(max_length=42)),
                ('end', geoposition.fields.GeopositionField(max_length=42)),
                ('route', models.ForeignKey(related_name='steps', to='core.DirectionsRoute')),
            ],
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('school_id', models.CharField(max_length=255)),
                ('school_name', models.CharField(max_length=255)),
                ('edu_type', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Friend',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('friend_id', models.CharField(max_length=255)),
                ('friend_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Hometown',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hometown_id', models.CharField(max_length=255)),
                ('hometown_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gender', models.IntegerField(blank=True, null=True, choices=[(1, b'Female'), (2, b'Male')])),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RequestMatch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('affinity', models.FloatField()),
                ('route_overlap', models.FloatField()),
                ('request1', models.ForeignKey(related_name='reqmatches1', to='core.CabRequest')),
                ('request2', models.ForeignKey(related_name='reqmatches2', to='core.CabRequest')),
            ],
        ),
        migrations.AddField(
            model_name='hometown',
            name='profile',
            field=models.OneToOneField(to='core.Profile'),
        ),
        migrations.AddField(
            model_name='friend',
            name='profile',
            field=models.ForeignKey(to='core.Profile'),
        ),
        migrations.AddField(
            model_name='education',
            name='profile',
            field=models.ForeignKey(to='core.Profile'),
        ),
        migrations.AddField(
            model_name='cabrequest',
            name='profile',
            field=models.ForeignKey(related_name='cabrequests', to='core.Profile'),
        ),
    ]
