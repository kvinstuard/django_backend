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
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    tipo_opciones = (
        ('VIAJE', 'VIAJE'),
        ('HOGAR', 'HOGAR'),
        ('PAREJA', 'PAREJA'),
        ('COMIDA', 'COMIDA'),
        ('OTRO', 'OTRO'),
    )
    tipo = models.CharField(max_length=10, choices=tipo_opciones)
    foto = models.CharField(max_length=250) #modificar por un campo que admita imagenes
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
    foto = models.CharField(max_length=100, null=True) #cambiar por foto
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
    descripcion = models.TextField(blank=True)
    valor = models.FloatField()  # Considerar cambiar a DecimalField para mayor precision.
    id_evento = models.ForeignKey(Evento, on_delete=models.CASCADE)

    def __str__(self):
        return self.descripcion

class ParticipantesEventoActividad(models.Model):
    id = models.AutoField(primary_key=True)
    id_actividad = models.ForeignKey(Actividades, on_delete=models.CASCADE)
    id_evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    id_participante = models.ForeignKey(Contactos, on_delete=models.CASCADE)
    valor_participacion = models.IntegerField()  

    def __str__(self):
        return f'{self.id_participante} - {self.id_actividad}'



