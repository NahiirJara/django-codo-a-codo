# Generated by Django 4.2.4 on 2023-10-21 01:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='estudiante',
            options={'verbose_name_plural': 'Estudiantes'},
        ),
        migrations.CreateModel(
            name='Proyecto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre')),
                ('nombre_slug', models.SlugField(max_length=100, unique=True, verbose_name='Nombre Slug')),
                ('anio', models.IntegerField(verbose_name='Año')),
                ('descripcion', models.TextField(null=True, verbose_name='Descripcion')),
                ('url', models.URLField(max_length=100, verbose_name='Url')),
                ('portada', models.ImageField(null=True, upload_to='imagenes/proyecto/', verbose_name='Portada')),
                ('estudiante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='administracion.estudiante')),
            ],
        ),
    ]