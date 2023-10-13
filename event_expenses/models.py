from django.db import models

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
    
    correo_electronico = models.EmailField(primary_key=True, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    apodo = models.CharField(max_length=100)
    foto = models.CharField(max_length=100) #cambiar por foto
    id_evento = models.ForeignKey(Evento, on_delete=models.SET_NULL, null=True, blank=True)
    #activo = models.BooleanField(default=True, editable=False)

    def __str__(self):
        return self.apodo

class Contactos(models.Model):
    id = models.AutoField(primary_key=True)
    correo_electronico_contacto = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return self.correo_electronico_contacto.correo_electronico

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



