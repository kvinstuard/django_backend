from rest_framework import serializers
from .models import Evento, Usuario, Contactos, Actividades, ParticipantesEventoActividad, User

# --------------------------------------------------------------------------------
#Convirtiendo los modelos en datos de python 
# --------------------------------------------------------------------------------

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__' 

class UsuarioSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Usuario
        fields = ('user', 'foto', 'id_evento')

class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = '__all__'

class ContactoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contactos
        fields = ('usuario', 'contacto')

class ContactoSerializerDetallado(serializers.ModelSerializer):
    usuario = UserSerializer() 
    contacto = UserSerializer()

    class Meta:
        model = Contactos
        fields = ('usuario', 'contacto')

class ActividadesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actividades
        fields = '__all__'

class ParticipantesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipantesEventoActividad
        fields = '__all__'