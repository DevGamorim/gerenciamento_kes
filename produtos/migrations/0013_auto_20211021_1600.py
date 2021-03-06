# Generated by Django 3.2.6 on 2021-10-21 19:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0012_auto_20211021_1413'),
    ]

    operations = [
        migrations.RenameField(
            model_name='opcao_cor',
            old_name='OC_ID',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='opcao_cor',
            old_name='OC_valor',
            new_name='valor',
        ),
        migrations.RenameField(
            model_name='opcao_envio',
            old_name='OE_ID',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='opcao_envio',
            old_name='OE_valor',
            new_name='valor',
        ),
        migrations.RenameField(
            model_name='opcao_escala_cor',
            old_name='OES_ID',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='opcao_escala_cor',
            old_name='OES_valor',
            new_name='valor',
        ),
        migrations.RenameField(
            model_name='opcao_localizacao',
            old_name='OL_ID',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='opcao_localizacao',
            old_name='OL_valor',
            new_name='valor',
        ),
        migrations.RenameField(
            model_name='opcao_material',
            old_name='OM_ID',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='opcao_material',
            old_name='OM_valor',
            new_name='valor',
        ),
        migrations.RenameField(
            model_name='opcao_material_acabamento',
            old_name='OMA_ID',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='opcao_material_acabamento',
            old_name='OMA_valor',
            new_name='valor',
        ),
        migrations.RenameField(
            model_name='opcao_material_especura',
            old_name='OME_ID',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='opcao_material_especura',
            old_name='OME_valor',
            new_name='valor',
        ),
        migrations.RenameField(
            model_name='opcao_material_pintura_suporte',
            old_name='OMPS_ID',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='opcao_material_pintura_suporte',
            old_name='OMPS_valor',
            new_name='valor',
        ),
        migrations.RenameField(
            model_name='opcao_material_suporte',
            old_name='OMS_ID',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='opcao_material_suporte',
            old_name='OMS_valor',
            new_name='valor',
        ),
        migrations.RenameField(
            model_name='opcao_possui_pes',
            old_name='OPP_ID',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='opcao_possui_pes',
            old_name='OPP_valor',
            new_name='valor',
        ),
        migrations.RenameField(
            model_name='opcao_tipo_fixacao',
            old_name='OTF_ID',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='opcao_tipo_fixacao',
            old_name='OTF_valor',
            new_name='valor',
        ),
        migrations.RenameField(
            model_name='opcao_tipo_suporte',
            old_name='OTS_ID',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='opcao_tipo_suporte',
            old_name='OTS_valor',
            new_name='valor',
        ),
        migrations.RenameField(
            model_name='opcao_tipo_tinta',
            old_name='OTT_ID',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='opcao_tipo_tinta',
            old_name='OTT_valor',
            new_name='valor',
        ),
        migrations.RenameField(
            model_name='opcao_verniz',
            old_name='OV_ID',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='opcao_verniz',
            old_name='OV_valor',
            new_name='valor',
        ),
    ]
