# Generated by Django 5.2.1 on 2025-05-29 02:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('servicios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Derivacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('observaciones', models.TextField(blank=True, null=True)),
                ('fecha_derivacion', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Derivación Médica',
                'verbose_name_plural': 'Derivaciones Médicas',
            },
        ),
        migrations.CreateModel(
            name='Cita',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('hora_inicio', models.TimeField()),
                ('estado', models.CharField(choices=[('Pendiente', 'Pendiente'), ('Atendido', 'Atendido'), ('Cancelado', 'Cancelado')], default='Pendiente', max_length=20)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('ultima_modificacion', models.DateTimeField(auto_now=True)),
                ('especialidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='citas_servicio', to='servicios.especialidadmedica')),
            ],
            options={
                'verbose_name': 'Cita Médica',
                'verbose_name_plural': 'Citas Médicas',
            },
        ),
    ]
