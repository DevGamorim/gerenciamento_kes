# Generated by Django 3.2.6 on 2021-09-30 13:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('produtos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sinc_open',
            fields=[
                ('SO_ID', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('SO_status', models.BooleanField()),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Sinc_Accs',
            fields=[
                ('SA_ID', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('SA_Nome', models.CharField(max_length=100)),
                ('SA_Senha', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sinc_Config',
            fields=[
                ('SC_ID', models.AutoField(primary_key=True, serialize=False)),
                ('SC_Nome', models.CharField(max_length=100)),
                ('SC_Key', models.CharField(max_length=300)),
                ('SC_ip', models.CharField(max_length=100)),
                ('SC_TempoExecucao', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Sinc_view',
            fields=[
                ('SV_ID', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('SV_Site', models.BooleanField()),
                ('SV_Omni', models.BooleanField()),
                ('SV_Master', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Sinc_log',
            fields=[
                ('SL_ID', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('SL_Nome', models.CharField(max_length=100)),
                ('SL_GetOrigem', models.CharField(max_length=100, null=True)),
                ('SL_PostSaida', models.CharField(max_length=100, null=True)),
                ('SL_PrecoDe', models.FloatField()),
                ('SL_PrecoPor', models.FloatField()),
                ('SL_Estoque', models.IntegerField()),
                ('SL_user', models.CharField(max_length=100, null=True)),
                ('SL_view', models.BooleanField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('SL_ProdutoID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='produtos.produto')),
            ],
        ),
    ]