# Generated by Django 2.2.8 on 2020-01-07 00:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OptionCorrelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('predicate_polarity', models.BooleanField()),
                ('correlation', models.FloatField(default=0.5)),
                ('predicate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='correlation_predicate', to='voting.BallotOption')),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='correlation_target', to='voting.BallotOption')),
            ],
            options={
                'unique_together': {('predicate', 'predicate_polarity', 'target')},
            },
        ),
    ]
