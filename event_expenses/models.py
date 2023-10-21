from django.db import models
from django.conf import settings
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

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
    id_usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

class Usuario(models.Model):
    email = models.EmailField(primary_key=True, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    password = models.CharField(max_length=300, default="dummy_password")
    apodo = models.CharField(max_length=100)
    foto = models.CharField(max_length=100) #cambiar por foto
    id_evento = models.ForeignKey(Evento, on_delete=models.SET_NULL, null=True, blank=True)
    #activo = models.BooleanField(default=True, editable=False)

    def __str__(self):
        return self.apodo
    
# ------------------------------------------------------------------------
# Esto hace que se cree un token automaticamente cuando se crea un usuario
# ------------------------------------------------------------------------

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

# ------------------------------------------------------------------------

class Contactos(models.Model):
    correo_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, related_name="contactos_usuario")
    correo_electronico_contacto = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, related_name="contactos_contacto")

    def __str__(self):
        return self.correo_electronico_contacto.correo_electronico
    
    class Meta:
        unique_together = (("correo_usuario", "correo_electronico_contacto"),)

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



