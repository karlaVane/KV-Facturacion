# Generated by Django 4.0.1 on 2022-01-14 22:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Facturacion', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='actualizaciones',
            old_name='fecha_pedido',
            new_name='ultima_fecha_pedido',
        ),
        migrations.RenameField(
            model_name='actualizaciones',
            old_name='num_pedido',
            new_name='ultimo_num_pedido',
        ),
    ]