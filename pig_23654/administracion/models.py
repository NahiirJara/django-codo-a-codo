from collections.abc import Iterable
from django.db import models
from django.db.models.query import QuerySet
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser

# Create your models here.
# Recomendado apenas se empieza a usar auth
# class PIGUser(AbstractUser):
#     pass


class Persona(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    apellido = models.CharField(max_length=150, verbose_name='Apellido')
    email = models.EmailField(max_length=150, null=True)
    dni = models.IntegerField(verbose_name="DNI")

    def __str__(self):
        return f"{self.dni} - {self.nombre}"


class EstudianteManager(models.Manager):
    def cantidad(self):
        return self.count()

    def get_queryset(self):
        return super().get_queryset().filter()


class Estudiante(Persona):
    matricula = models.CharField(max_length=10, verbose_name='Matricula')
    baja = models.BooleanField(default=False)
    objects = EstudianteManager()

    def __str__(self):
        return f"{self.matricula} - {self.nombre} {self.apellido}"

    def soft_delete(self):
        self.baja = True
        super().save()

    def restore(self):
        self.baja = False
        super().save()

    def obtener_baja_url(self):
        return reverse_lazy('estudiante_baja', args=[self.id])

    def obtener_modificacion_url(self):
        return reverse_lazy('estudiante_modificacion', args=[self.id])

    class Meta():
        verbose_name_plural = 'Estudiantes'
        # db_table = 'nombre_tabla'


class DocenteManager(models.Manager):
    def cantidad(self):
        return self.count()

    def get_queryset(self):
        return super().get_queryset().filter(baja=False)


class Docente(Persona):
    legajo = models.CharField(max_length=10, verbose_name='Legajo')
    baja = models.BooleanField(default=False)
    objects = DocenteManager()

    def __str__(self):
        return f"{self.legajo} - {self.nombre} {self.apellido}"
    
    def obtener_baja_url(self):
        return reverse_lazy('docente_baja', args=[self.id])

    def obtener_modificacion_url(self):
        return reverse_lazy('docente_modificacion', args=[self.id])


class Categoria(models.Model):
    nombre = models.CharField(max_length=50, verbose_name='Nombre')
    baja = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

    def soft_delete(self):
        self.baja = True
        super().save()

    def restore(self):
        self.baja = False
        super().save()

    # def save(self):
    #     if  "django" in self.nombre.lower():
    #         raise ValueError("QUE HACES?? NO PUEDE HABER MAS DJANGO")
    #     else:
    #         return super().save()

    # def delete(self):
    #     self.soft_delete()


class Curso(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(null=True, verbose_name='Descripcion')
    fecha_inicio = models.DateField(verbose_name='Fecha de inicio', null=True, default=None)
    portada = models.ImageField(upload_to='imagenes/', null=True, verbose_name='Portada')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)  # relacion mucho a uno

    def __str__(self):
        return self.nombre

    def delete(self, using=None, keep_parents=False):
        self.portada.storage.delete(self.portada.name)  # borrado fisico
        super().delete()

    


class Comision(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    horario = models.CharField(max_length=100, verbose_name="Horario", null=True, default=None)
    link_meet = models.URLField(max_length=100, verbose_name='Link de Meet', null=True, default=None)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)  # relacion mucho a uno
    estudiantes = models.ManyToManyField(Estudiante, through='Inscripcion')

    class Meta:
        verbose_name_plural = "Comisiones"

    def __str__(self):
        return f"{self.curso} - {self.nombre}"
    
    def obtener_baja_url(self):
        return reverse_lazy('comision_baja', args=[self.id])

    def obtener_modificacion_url(self):
        return reverse_lazy('comision_modificacion', args=[self.id])


class InscriptosManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(estado=Inscripcion.Estado.INSCRIPTO)


class CursandoManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(estado=Inscripcion.Estado.CURSANDO)


class EgresadosManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(estado=Inscripcion.Estado.EGRESADO)


class Inscripcion(models.Model):
    # ESTADOS = [
    #     (1, 'Inscripto'),
    #     (2, 'Cursando'),
    #     (3, 'Egresado'),
    # ]
    # Opción mas actual con clase choice
    class Estado(models.TextChoices):
        INSCRIPTO = 'INS', 'Inscripto'
        CURSANDO = 'CUR', 'Cursando'
        EGRESADO = 'EGR', 'Egresado'

    fecha_creacion = models.DateField(auto_now_add=True, verbose_name='Fecha de creacion')
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    comision = models.ForeignKey(Comision, on_delete=models.CASCADE)
    # estado = models.IntegerField(choices=ESTADOS, default=1)
    # Opción mas actual con clase choice
    estado = models.CharField(max_length=3, choices=Estado.choices, default=Estado.INSCRIPTO)
    inscripciones_totales = models.Manager()
    inscriptos = InscriptosManager()
    cursando = CursandoManager()
    egresados = EgresadosManager()

    def __str__(self):
        return self.estudiante.nombre
    
    def obtener_baja_url(self):
        return reverse_lazy('inscripcion_baja', args=[self.id])

    def obtener_modificacion_url(self):
        return reverse_lazy('inscripcion_modificacion', args=[self.id])
    
class Proyecto(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    # campo del tipo slug
    nombre_slug = models.SlugField(max_length=100, verbose_name='Nombre Slug', null=False, unique=True)
    anio = models.IntegerField(verbose_name='Año')
    descripcion = models.TextField(null=True, verbose_name='Descripcion')
    url = models.URLField(max_length=100, verbose_name='Url')
    portada = models.ImageField(upload_to='imagenes/proyecto/', null=True, verbose_name='Portada')
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        self.nombre_slug = slugify(f"{self.anio}-{self.nombre}")
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        self.portada.storage.delete(self.portada.name)  # borrado fisico
        super().delete()

    def obtener_baja_url(self):
        return reverse_lazy('proyecto_baja', args=[self.id])

    def obtener_modificacion_url(self):
        return reverse_lazy('proyecto_modificacion', args=[self.id])


class Lenguaje(models.Model):
    nombre = models.CharField(verbose_name="Nombre:", max_length=100)
    logo = models.ImageField(verbose_name="Image:", upload_to="logos/")

    def __str__(self) -> str:
        return self.nombre