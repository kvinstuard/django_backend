from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from django.http import HttpResponse
from .serializer import UsuarioSerializer, ContactoSerializer, EventoSerializer, ActividadesSerializer, ParticipantesSerializer, ContactoSerializerDetallado, UserSerializer
from .models import Usuario, Contactos, Evento, Actividades, ParticipantesEventoActividad, User
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken, AuthTokenSerializer
from rest_framework.settings import api_settings
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import post_save
from django.core import serializers
import json
import random

# --------------------------------------------------------------------------------
# Creando el CRUD
# Todas las vistas acá seran para crear y ver los modelos
# --------------------------------------------------------------------------------

# Método para crear un usuario.
# Primero crea un usuario de la relación "User" y luego se le asocian los argumentos
# que falten a la relación "Usuario"

@api_view(['GET','POST']) # Es un decorador que me sirve para renderizar en pantalla la vista basada en función.
def crear_usuario(request):
    if request.method == 'GET':
        usuarios = Usuario.objects.all()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        # Creamos el usuario (User)
        user = User.objects.create(
            email = request.data["email"],
            first_name = request.data["nombres"],
            last_name = request.data["apellidos"],
            password = request.data["password"],
            username = request.data["apodo"],
            is_active = True,
        )
        # Creamos su Token
        token = Token.objects.create(
            user=user
        )
        # Asociamos dicho usuario (User) a la relación Usuario.
        # Se debe actualizar porque ya se crea automaticamente el Usuario asociado
        # a la relación "user".
        usuario = Usuario.objects.get(
            user = user
        )
        usuario.foto = request.data["foto"]
        serializer = UsuarioSerializer(usuario, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# Método para modificar un usuario
# La solicitud debe ser de tipo "PUT"

@api_view(['PUT', 'POST']) # Es un decorador que me sirve para renderizar en pantalla la vista basada en función.
def modificar_usuario(request):
    if request.method == 'PUT':
        try:
            user_obj = User.objects.get(email=request.data["email"])
        except User.DoesNotExist:
            return Response({"error": True, "error_cause": 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        try:
            usuario_obj = Usuario.objects.get(user=user_obj)
        except Usuario.DoesNotExist:
            return Response({"error": True, "error_cause": 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        # Actualiza los campos del usuario 'user_obj' con los datos de la solicitud
        # user_obj.email = request.data["email"]
        user_obj.first_name = request.data["nombres"] 
        user_obj.last_name = request.data["apellidos"]
        user_obj.password = request.data["password"]
        # user_obj.username = request.data["apodo"] 
        user_obj.is_active = request.data["is_active"]
        user_obj.save()
        
        # Actualiza los campos del usuario 'usuario_obj' con los datos de la solicitud
        usuario_obj.foto = request.data["foto"]
        usuario_obj.save()

        return Response({"error": False, "description": 'Datos del usuario actualizados!'}, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        try:
            user = User.objects.get(email=request.data["email"])
        except User.DoesNotExist:
            return Response({"error": True, "error_cause": 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        try:
            usuario = Usuario.objects.get(user=user)
        except Usuario.DoesNotExist:
            return Response({"error": True, "error_cause": 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        user_data = {
            "email": user.email,
            "nombres": user.first_name,
            "apellidos": user.last_name,
            "password": user.password,
            "apodo": user.username,
            "foto": usuario.foto,
            "is_active": user.is_active,
        }
        return Response(user_data, status=status.HTTP_200_OK)
    else:
        return Response({"error": True, "error_cause": 'Invalid request method!'}, status=status.HTTP_400_BAD_REQUEST)
    
    
class ContactoViews(viewsets.ModelViewSet):
    serializer_class = ContactoSerializerDetallado
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
# Registro y Login
# --------------------------------------------------------------------------------

# Método para que un usuario se logee
@api_view(['POST'])
def login_user(request):
    print("user:",request.data) 
    try:
        user = User.objects.get(email=request.data["email"], password=request.data["password"])
    except User.DoesNotExist:
        return Response({"error": True, "error_cause": 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
    token = Token.objects.get(user=user)
    try:
        usuario = Usuario.objects.get(user=user)
    except Usuario.DoesNotExist:
        return Response({"error": True, "error_cause": 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    # Serializa el objeto 'usuario'
    usuario_serializer = UsuarioSerializer(usuario, many=False)

    reqdata = {
        "token": token.key,
        "user_details": usuario_serializer.data,
    }
    return Response({"answer": True, "description": reqdata }, status=status.HTTP_200_OK)

# --------------------------------------------------------------------------------
# Gestión de contactos
# --------------------------------------------------------------------------------

# Para agregar un contacto

@api_view(['POST']) # Es un decorador que me sirve para renderizar en pantalla la vista basada en función.
def agregar_contacto(request):
    correo_usuario = request.data["correo_usuario"]
    correo_contacto = request.data["correo_contacto"]
    # Determinamos si el usuario existe
    try:
        user = User.objects.get(email=correo_usuario)
    except User.DoesNotExist:
        return Response({"error":True, "error_causa":"El usuario no existe!"}, status=status.HTTP_404_NOT_FOUND)
    
    # Determinamos si el contacto existe.
    try:
        contact = User.objects.get(email=correo_contacto)
    except User.DoesNotExist:
        return Response({"error":True, "error_causa":"El usuario-contacto no existe!"}, status=status.HTTP_404_NOT_FOUND)

    # Determinamos si el usuario tiene agregado el contacto.
    # Si no existe lo crea y lo agrega.
    try:
        contacto = Contactos.objects.get(usuario=user, contacto=contact)
        return Response({"error":True, "mensaje":"El usuario ya tiene agregado el contacto!"}, status=status.HTTP_400_BAD_REQUEST)
    except Contactos.DoesNotExist:
        contacto_nuevo =    {
            'usuario': user.id,
            'contacto': contact.id
        }
        serializer = ContactoSerializer(data=contacto_nuevo)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            contacto = Contactos(**validated_data)
            contacto.save()
            serializer_response = ContactoSerializer(contacto)
            return Response(serializer_response.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"error":True, "mensaje":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# Para eliminar un contacto

@api_view(['POST'])
def eliminar_contacto(request):
    correo_usuario = request.data["correo_usuario"]
    correo_contacto = request.data["correo_contacto"]
    # Determinamos si el usuario existe
    try:
        user = User.objects.get(email=correo_usuario)
    except User.DoesNotExist:
        return Response({"error":True, "error_causa":"El usuario no existe!"}, status=status.HTTP_404_NOT_FOUND)
    
    # Determinamos si el contacto existe.
    try:
        contact = User.objects.get(email=correo_contacto)
    except User.DoesNotExist:
        return Response({"error":True, "error_causa":"El usuario-contacto no existe!"}, status=status.HTTP_404_NOT_FOUND)

    # Determinamos si el usuario tiene agregado el contacto.
    # Si no lo tiene agregado arroja un error.
    try:
        contacto = Contactos.objects.get(usuario=user, contacto=contact)
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
        evento = Evento.objects.get(id_usuario=contact)
        return Response({"error":True, "mensaje":"El contacto tiene un evento creado; evento: '{nombre_evento}'".format(nombre_evento=evento.nombre)}, status=status.HTTP_400_BAD_REQUEST)
    except Evento.DoesNotExist:
        print("El contacto no tiene un evento creado!")

    # consultamos la tabla "ParticipantesEventoActividad", para ver si el contacto
    # ha sido agregado a un evento.
    try:
        participantes_eventos = ParticipantesEventoActividad.objects.get(id_participante=contacto)
        return Response({"error":True, "mensaje":"El contacto está asociado a una actividad de un evento; actividad: '{nombre_actividad}', evento: '{nombre_evento}'".format(nombre_actividad=participantes_eventos.id_actividad.descripcion, nombre_evento=participantes_eventos.id_evento.nombre)}, status=status.HTTP_400_BAD_REQUEST)
    except ParticipantesEventoActividad.DoesNotExist:
        print("El contacto no está agregado a alguna actividad de un evento!")
    
    # Finalmente, si pasa todas las pruebas, se elimina el contacto.
    contacto.delete()
    return Response({"error":False, "mensaje":"El usuario-contacto fue eliminado éxitosamente!"}, status=status.HTTP_200_OK)

# Listar contactos de un usuario especifico

@api_view(['POST'])
def listar_contactos(request):
    # Determinamos si el usuario existe
    try:
        user = User.objects.get(email=request.data["email"])
    except User.DoesNotExist:
        return Response({"error":True, "error_causa":"El usuario no existe!"}, status=status.HTTP_404_NOT_FOUND)

    # Buscamos los eventos creados por el usuario
    try:
        contactos = Contactos.objects.filter(usuario=user) 
    except Contactos.DoesNotExist:
        return Response({ "contactos" : [], "message": "El usuario no tiene contactos!"  }, status=status.HTTP_200_OK)
    
    # Ahora extraemos los datos de cada contacto
    lista_contactos = []
    for contacto in contactos:
        try:
            usuario = Usuario.objects.get(user=contacto.contacto)
        except Usuario.DoesNotExist:
            return Response({"error": True, "error_cause": 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        contact = {
            "email": contacto.contacto.email,
            "nombre": contacto.contacto.first_name,
            "apodo": contacto.contacto.username,
            "avatar": usuario.foto,
        } 
        lista_contactos.append(contact)
    print("lista_contactos:", lista_contactos)
    contactos_data = { "contactos" : lista_contactos, "message": "Ok!"  }

    return Response(contactos_data, status=status.HTTP_200_OK)
    

# Listar contactos de un usuario especifico por evento

@api_view(['POST'])
def listar_contactos_evento(request):
    # Determinamos si el usuario existe
    try:
        user = User.objects.get(email=request.data["email"])
    except User.DoesNotExist:
        return Response({"error":True, "error_causa":"El usuario no existe!"}, status=status.HTTP_404_NOT_FOUND)

    # Buscamos los eventos creados por el usuario
    try:
        eventos = Evento.objects.filter(id_usuario=user) 
    except Evento.DoesNotExist:
        return Response({ "contactos" : [], "message": "El usuario no tiene eventos creados!"  }, status=status.HTTP_200_OK)
    
    # Ahora extraemos los datos de cada contacto
    print("eventos:", eventos)
    lista_contactos = []
    for evento in eventos:
        print("evento:", evento)
        # Buscamos el/los eventos creados por el usuario
        # a los que esté asociado el contacto
        try:
            eventosActividades = ParticipantesEventoActividad.objects.filter(id_evento=evento)
        except ParticipantesEventoActividad.DoesNotExist:
            print("No hay contactos asociados al evento:", evento.nombre)
        print("eventosActividades:", eventosActividades)        
        for eventoActividad in eventosActividades:
            contact = {
                "email": eventoActividad.id_participante.contacto.email,
                "nombre": eventoActividad.id_participante.contacto.first_name,
                "evento": eventoActividad.id_evento.nombre,
                "actividad": eventoActividad.id_actividad.descripcion,
                "saldo": eventoActividad.valor_participacion,
            } 
            lista_contactos.append(contact)
    print("lista_contactos:", lista_contactos)
    contactos_data = { "contactos" : lista_contactos, "message": "Ok!"  }

    return Response(contactos_data, status=status.HTTP_200_OK)
    
# --------------------------------------------------------------------------------
# Experimental
# --------------------------------------------------------------------------------

@api_view(['POST'])
def UsuarioSingUpViews(request):
    serializer = UsuarioSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        #user = User.objects.get(username=request.data['correo_electronico'])#username en comillas
        #user.set_password(request.data['password'])
        #user.save()
        #token = Token.objects.create(user=user)
        user = Usuario.objects.create(
            correo_electronico=request.data['correo_electronico'],
            password=request.data['password'],
            nombres=request.data['nombres'],
            apellidos=request.data['apellidos'],
            apodo=request.data['apodo'],
            foto=request.data['foto']
            
        )
        token = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def UsuarioLoginViews(request):
    return Response({})

@api_view(['GET'])
def TestToken(request):
    return Response({})
##