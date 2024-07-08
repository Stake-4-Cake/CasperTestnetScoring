# Generated by Django 5.0.6 on 2024-07-08 10:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField(verbose_name='IP Address')),
                ('public_key', models.CharField(default='', max_length=128, verbose_name='Public Key')),
                ('height', models.BigIntegerField(default=0, verbose_name='Height')),
                ('network_weight', models.BigIntegerField(default=0, verbose_name='Network Weight')),
                ('total_stake', models.BigIntegerField(default=0, verbose_name='Total Stake')),
                ('active_bid', models.BooleanField(default=False, verbose_name='Active Bid')),
                ('percent_of_network', models.FloatField(default=0, verbose_name='Percent Of Network')),
            ],
            options={
                'verbose_name': 'Node',
                'verbose_name_plural': 'Nodes',
                'ordering': ('-total_stake', '-height'),
            },
        ),
        migrations.CreateModel(
            name='Scoring',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_key', models.CharField(max_length=128, verbose_name='Public Key')),
                ('type', models.CharField(choices=[('D', 'Day'), ('W', 'Week'), ('Q', 'Quarter')], default='D', max_length=1, verbose_name='Type')),
                ('score', models.FloatField(default=0, verbose_name='Score')),
                ('longevity', models.FloatField(default=0, verbose_name='Longevity')),
                ('stake_over', models.BooleanField(default=False, verbose_name='Stake Over')),
                ('eligible_for_rewards', models.BooleanField(default=False, verbose_name='Eligible for Rewards')),
                ('timestamp', models.CharField(max_length=128, verbose_name='Timestamp')),
            ],
            options={
                'verbose_name': 'Scoring',
                'verbose_name_plural': 'Scoring',
                'ordering': ('-score', '-longevity'),
            },
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_block', models.BigIntegerField(default=0, verbose_name='Current Block')),
                ('network_weight', models.BigIntegerField(default=0, verbose_name='Network Weight')),
                ('total_stake', models.BigIntegerField(default=0, verbose_name='Total Stake')),
                ('active_bid', models.BooleanField(default=False, verbose_name='Active Bid')),
                ('percent_of_network', models.FloatField(default=0, verbose_name='Percent Of Network')),
                ('active', models.BooleanField(default=False, verbose_name='Active')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')),
                ('node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.node', verbose_name='Node')),
            ],
            options={
                'verbose_name': 'Score',
                'verbose_name_plural': 'Scores',
                'ordering': ('-current_block', '-total_stake'),
            },
        ),
    ]
