from django.db import models
from django.conf import settings
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

# ----------------------------------------------------------------------
# Creación de Modelos:
# ----------------------------------------------------------------------
# Cada uno es una abstracción de una tabla en BD sqlite.
# Recordemos que usamos la arquitectura MVT.
# Las vistas consultadas después de la URL, estás consultan los modelos (tablas)
# para así brindar datos de la BD hacía la vista y esta la lleve al template y
# este lo pase al browser.
# ----------------------------------------------------------------------

class Evento(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    tipo_opciones = (
        ('VIAJE', 'VIAJE'),
        ('HOGAR', 'HOGAR'),
        ('PAREJA', 'PAREJA'),
        ('COMIDA', 'COMIDA'),
        ('OTRO', 'OTRO'),
    )
    tipo = models.CharField(max_length=100, choices=tipo_opciones)
    foto = models.CharField(max_length=3100) #modificar por un campo que admita imagenes
    # En este campo va el dueño del evento
    id_usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

# Este modelo (tabla) se dejará como una extensión para agregar la foto del usuario.
# La mayor parte de los datos del usuario estarán disponibles en "User" de Django.

class Usuario(models.Model):
    # Este atributo (user) permite la relación uno a uno con auth_user,
    # un modelo en el que se guardan primer nombre, apellidos, nombre de usuario, 
    # correo, si está activo o no y contraseña del usuario.
    # sirve para vincular al usuario con un Token y así autenticarlo.
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, default=None)
    foto = models.CharField(max_length=3100, null=True) #cambiar por foto
    id_evento = models.ForeignKey(Evento, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username
    
# Definir una función que se ejecutará cuando se cree un nuevo usuario.
@receiver(post_save, sender=User)
def create_user_usuario_detalles(sender, instance, created, **kwargs):
    if created:
        Usuario.objects.create(user=instance)

# Conectar la señal al modelo User.
post_save.connect(create_user_usuario_detalles, sender=User)

class Contactos(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="contactos_usuario")
    contacto = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="contactos_contacto")
    
    def __str__(self):
        return f'{self.contacto.username} - {self.usuario.username}'
    
    class Meta:
        unique_together = (("usuario", "contacto"),)

class Actividades(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.TextField(blank=True, unique=True)
    # Este es el valor total de la actividad
    valor = models.DecimalField(max_digits=20, decimal_places=2)  
    id_evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    # En este campo va el dueño de la actividad
    id_usuario = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.descripcion

class ParticipantesEventoActividad(models.Model):
    id = models.AutoField(primary_key=True)
    id_actividad = models.ForeignKey(Actividades, on_delete=models.CASCADE, null=True)
    id_evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    # Con este campo se sabe también quienes son contactos de un evento.
    id_participante = models.ForeignKey(User, on_delete=models.CASCADE)
    # Este es el valor que aporta cada participante, no debe superar el valor de la actividad,
    # La idea es siempre mostrar el valor como número, no como porcentaje, solo se permite dar un %
    # al creador para el aporte que dará su contacto, pero el sistema calcula automaticamente el valor
    # númerico y lo asigna.
    valor_participacion = models.DecimalField(max_digits=20, decimal_places=2)
    # este campo es para saber si la negociacion de la actividad se hizo con porcentaje o valor fijo
    # Será un porcentaje que se guardará acá, si es un monto no se guarda nada en esta variable.
    valor_participacion_porcentaje = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    valor_pagado = models.DecimalField(max_digits=20, decimal_places=2, default=0.0000) 
    # Este campo servirá para validar si el participante aceptó participar 
    aceptado = models.BooleanField(null=False, default=False)
    fecha_aceptacion = models.DateTimeField(null=True)

    def __str__(self):
        return f'{self.id_participante} - {self.id_actividad}'



