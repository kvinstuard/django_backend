from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from django.http import HttpResponse
from .serializer import UsuarioSerializer, ContactoSerializer, EventoSerializer, ActividadesSerializer, ParticipantesSerializer
from .models import Usuario, Contactos, Evento, Actividades, ParticipantesEventoActividad
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken, AuthTokenSerializer
from rest_framework.settings import api_settings
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import post_save

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
#    lookup_field = 'email' 
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

# creacion o autenticacion del token
class CreateTokenView(ObtainAuthToken):
    """Create auth token"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'error': False,
                'token': token.key,
                'email': user.email,
                'name': user.nombre,
            })
        else:
            return Response({"error": True}, status=status.HTTP_200_OK)

# --------------------------------------------------------------------------------
# Registro y Login
# --------------------------------------------------------------------------------

# Método para que un usuario se logee
@api_view(['POST'])
def login_user(request):
    print("user:",request.data) 
    try:
        usuario = Usuario.objects.get(email=request.data["email"], password=request.data["password"])
    except Usuario.DoesNotExist:
        return Response({"error": True, "error_cause": 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
    # token = Token.objects.get(user=usuario)
    reqdata = {
        "token": "testToken 48712847124sj81%324",
        "nickname": usuario.apodo
    }
    return Response({"answer": True, "description": reqdata }, status=status.HTTP_200_OK)

# creacion del token que permitira al usuario acceder a su url respectiva
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

# --------------------------------------------------------------------------------
# Gestión de contactos
# --------------------------------------------------------------------------------

# Para agregar un contacto

@api_view(['GET','POST']) # Es un decorador que me sirve para renderizar en pantalla la vista basada en función.
def agregar_contacto(request, correo_usuario, correo_contacto):
    # Determinamos si el usuario existe
    try:
        usuario = Usuario.objects.get(email=correo_usuario)
    except Usuario.DoesNotExist:
        return Response({"error":True, "error_causa":"El usuario no existe!"}, status=status.HTTP_404_NOT_FOUND)
    
    # Determinamos si el contacto existe.
    try:
        usuario = Usuario.objects.get(email=correo_contacto)
    except Usuario.DoesNotExist:
        return Response({"error":True, "error_causa":"El usuario-contacto no existe!"}, status=status.HTTP_404_NOT_FOUND)

    # Determinamos si el usuario tiene agregado el contacto.
    # Si no existe lo crea y lo agrega.
    try:
        contacto = Contactos.objects.get(correo_usuario=correo_usuario, correo_electronico_contacto=correo_contacto)
        return Response({"error":True, "mensaje":"El usuario ya tiene agregado el contacto!"}, status=status.HTTP_400_BAD_REQUEST)
    except Contactos.DoesNotExist:
        contacto_nuevo =    {
            'correo_usuario':correo_usuario,
            'correo_electronico_contacto': correo_contacto   
        }
        serializer = ContactoSerializer(data=contacto_nuevo)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            contacto = Contactos(**validated_data)
            contacto.save()
            serializer_response = ContactoSerializer(contacto)
            return Response(serializer_response.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"error":True, "mensaje":serializer.error_messages}, status=status.HTTP_400_BAD_REQUEST)

# Para eliminar un contacto

@api_view(['GET','POST'])
def eliminar_contacto(request, correo_usuario, correo_contacto):
    # Determinamos si el usuario existe
    try:
        usuario = Usuario.objects.get(email=correo_usuario)
    except Usuario.DoesNotExist:
        return Response({"error":True, "error_causa":"El usuario no existe!"}, status=status.HTTP_404_NOT_FOUND)
    
    # Determinamos si el usuario tiene agregado el contacto.
    # Si no lo tiene agregado arroja un error.
    try:
        contacto = Contactos.objects.get(correo_usuario=correo_usuario, correo_electronico_contacto=correo_contacto)
    except Contactos.DoesNotExist:
        return Response({"error":True, "mensaje":"El usuario-contacto no está agregado en la lista de contactos del usuario!"}, status=status.HTTP_404_NOT_FOUND)

    # Determinamos si el usuario tiene un evento asociado
    """
    Un usuario está asociado a un evento si:
    - El usuario no ha creado algún evento.
    - El usuario no ha sido agregado a alguna actividad de un evento.
    """
    # consultamos la tabla "Evento", para ver si el contacto creó un evento.
    try:
        evento = Evento.objects.get(id_usuario=correo_contacto)
        return Response({"error":True, "mensaje":"El contacto tiene un evento creado; evento: '{nombre_evento}'".format(nombre_evento=evento.nombre)}, status=status.HTTP_400_BAD_REQUEST)
    except Evento.DoesNotExist:
        print("El contacto no tiene un evento creado!")

    # consultamos la tabla "ParticipantesEventoActividad", para ver si el contacto
    # ha sido agregado a un evento.
    try:
        participantes_eventos = ParticipantesEventoActividad.objects.get(id_participante=contacto.id)
        return Response({"error":True, "mensaje":"El contacto está asociado a una actividad de un evento; actividad: '{nombre_actividad}', evento: '{nombre_evento}'".format(nombre_actividad=participantes_eventos.id_actividad.descripcion, nombre_evento=participantes_eventos.id_evento.nombre)}, status=status.HTTP_400_BAD_REQUEST)
    except ParticipantesEventoActividad.DoesNotExist:
        print("El contacto no está agregado a alguna actividad de un evento!")
    
    # Finalmente, si pasa todas las pruebas, se elimina el contacto.
    contacto.delete()
    return Response({"error":True, "mensaje":"El usuario-contacto fue eliminado éxitosamente!"}, status=status.HTTP_200_OK)