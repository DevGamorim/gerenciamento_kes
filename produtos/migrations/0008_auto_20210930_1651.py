# Generated by Django 3.2.6 on 2021-09-30 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0007_alter_correcoes_cr_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='correcoes',
            name='CR_motivo_correcao_1',
        ),
        migrations.RemoveField(
            model_name='correcoes',
            name='CR_motivo_correcao_2',
        ),
        migrations.RemoveField(
            model_name='correcoes',
            name='CR_motivo_correcao_3',
        ),
        migrations.RemoveField(
            model_name='correcoes',
            name='CR_motivo_correcao_4',
        ),
        migrations.RemoveField(
            model_name='correcoes',
            name='CR_motivo_correcao_5',
        ),
        migrations.AddField(
            model_name='correcoes',
            name='CR_links',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='correcoes',
            name='CR_motivo_correcao',
            field=models.TextField(null=True),
        ),
    ]