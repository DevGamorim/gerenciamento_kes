# Generated by Django 3.2.6 on 2021-09-30 13:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0002_correcoes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='correcao_log',
            name='CL_correcao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='produtos.correcoes'),
        ),
        migrations.DeleteModel(
            name='Correcao',
        ),
    ]
