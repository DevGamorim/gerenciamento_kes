# Generated by Django 3.2.6 on 2021-09-30 13:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0003_auto_20210930_1045'),
    ]

    operations = [
        migrations.CreateModel(
            name='Correcoes_log',
            fields=[
                ('CL_id', models.IntegerField(primary_key=True, serialize=False)),
                ('CL_campo', models.CharField(max_length=100, null=True)),
                ('CL_valor_antigo', models.CharField(max_length=100, null=True)),
                ('CL_valor_novo', models.CharField(max_length=100, null=True)),
                ('CL_user', models.CharField(max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('CL_correcao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='produtos.correcoes')),
                ('CL_produto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='produtos.produto')),
            ],
        ),
    ]