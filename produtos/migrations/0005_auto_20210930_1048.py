# Generated by Django 3.2.6 on 2021-09-30 13:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0004_correcoes_log'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='correcoes_log',
            name='CL_correcao',
        ),
        migrations.RemoveField(
            model_name='correcoes_log',
            name='CL_produto',
        ),
        migrations.DeleteModel(
            name='Correcao_log',
        ),
        migrations.DeleteModel(
            name='Correcoes_log',
        ),
    ]
