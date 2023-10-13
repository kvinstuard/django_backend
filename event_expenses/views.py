from rest_framework import viewsets, response, status
from django.http import HttpResponse
from .serializer import UsuarioSerializer, ContactoSerializer, EventoSerializer, ActividadesSerializer, ParticipantesSerializer
from .models import Usuario, Contactos, Evento, Actividades, ParticipantesEventoActividad

# --------------------------------------------------------------------------------
# Creando el CRUD
# Todas las vistas acá seran para crear y ver los modelos
# --------------------------------------------------------------------------------

class UsuarioViews(viewsets.ModelViewSet):
    serializer_class = UsuarioSerializer
    queryset = Usuario.objects.all()

#class UsuarioDetailView(generics.RetrieveAPIView):
#    queryset = Usuario.objects.all()
#    serializer_class = UsuarioSerializer
#    lookup_field = 'correo_electronico' 
#Tryng to get the user by email


class ContactoViews(viewsets.ModelViewSet):
    serializer_class = ContactoSerializer
    queryset = Contactos.objects.all()

class EventoViews(viewsets.ModelViewSet):
    serializer_class = EventoSerializer
    queryset = Evento.objects.all()

class ActividadesViews(viewsets.ModelViewSet):
    serializer_class = ActividadesSerializer
    queryset = Actividades.objects.all()
    
class ParticipantesViews(viewsets.ModelViewSet):
    serializer_class = ParticipantesSerializer
    queryset = ParticipantesEventoActividad.objects.all()

# --------------------------------------------------------------------------------
# Gestión de contactos
# --------------------------------------------------------------------------------

def agregar_contacto(request, correo_usuario, correo_contacto):
    # Determinamos si el usuario existe
    try:
        usuario = Usuario.objects.get(correo_electronico=correo_usuario)
    except Usuario.DoesNotExist:
        return response({"error","El usuario no existe!"}, status=status.HTTP_400_OK)
    
    # Determinamos si el contacto existe
    try:
        contacto = Contactos.objects.get(correo_electronico_contacto=correo_contacto)
        return response({"error","El contacto del usuario ya existe!"}, status=status.HTTP_400_OK)
    
    except Usuario.DoesNotExist:
        return response({"error","El contacto del usuario no existe!"}, status=status.HTTP_400_OK)