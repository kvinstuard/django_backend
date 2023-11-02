from rest_framework import serializers
from .models import Evento, Usuario, Contactos, Actividades, ParticipantesEventoActividad
from django.contrib.auth.models import User

# --------------------------------------------------------------------------------
#Convirtiendo los modelos en datos de python 
# --------------------------------------------------------------------------------

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['correo_electronico', 'password','nombres','apellidos','apodo','foto']



class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = '__all__'

class ContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contactos
        fields = '__all__'

class ActividadesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actividades
        fields = '__all__'

class ParticipantesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipantesEventoActividad
        fields = '__all__'