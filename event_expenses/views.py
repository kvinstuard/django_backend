from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from django.http import HttpResponse
from .serializer import UsuarioSerializer, ContactoSerializer, EventoSerializer, ActividadesSerializer, ParticipantesSerializer, ContactoSerializerDetallado, UserSerializer
from .models import Usuario, Contactos, Evento, Actividades, ParticipantesEventoActividad, User
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
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
        usuario.save()
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

        return Response({"error": False, "description": 'User data upgraded!'}, status=status.HTTP_200_OK)
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

@api_view(['POST']) # Es un decorador que me sirve para renderizar en pantalla la vista basada en función.
@authentication_classes([TokenAuthentication]) # Me sirve para permitir autenticación por token para acceder a este método.
@permission_classes([IsAuthenticated])
def crear_evento(request):
    if request.method == 'POST':
        # Obtenemos al usuario por medio de su token
        try:
            user = Token.objects.get(key=request.auth.key).user
        except Token.DoesNotExist:
            return Response({"error": True, "error_cause": 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        # Creamos el evento a partir del usuario
        request_data = {
            "nombre": request.data["nombre"],
            "descripcion": request.data["descripcion"],
            "tipo": request.data["tipo"],
            "foto": request.data["foto"],
            "id_usuario": user.id
        }
        serializer = EventoSerializer(data=request_data, many=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"error":True, "error_cause":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error": True, "error_cause": 'Invalid request method!'}, status=status.HTTP_400_BAD_REQUEST) 

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
        return Response({"error":True, "error_cause":"User does not exist!"}, status=status.HTTP_404_NOT_FOUND)
    
    # Determinamos si el contacto existe.
    try:
        contact = User.objects.get(email=correo_contacto)
    except User.DoesNotExist:
        return Response({"error":True, "error_cause":"User-contact not found!"}, status=status.HTTP_404_NOT_FOUND)

    # Determinamos si el usuario tiene agregado el contacto.
    # Si no existe lo crea y lo agrega.
    try:
        contacto = Contactos.objects.get(usuario=user, contacto=contact)
        return Response({"error":True, "error_cause":"Contact already exists!"}, status=status.HTTP_400_BAD_REQUEST)
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
            return Response({"error":True, "error_cause":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# Para eliminar un contacto

@api_view(['POST'])
def eliminar_contacto(request):
    correo_usuario = request.data["correo_usuario"]
    correo_contacto = request.data["correo_contacto"]
    # Determinamos si el usuario existe
    try:
        user = User.objects.get(email=correo_usuario)
    except User.DoesNotExist:
        return Response({"error":True, "error_cause":"User does not exist!"}, status=status.HTTP_404_NOT_FOUND)
    
    # Determinamos si el contacto existe.
    try:
        contact = User.objects.get(email=correo_contacto)
    except User.DoesNotExist:
        return Response({"error":True, "error_cause":"User-contact not found!"}, status=status.HTTP_404_NOT_FOUND)

    # Determinamos si el usuario tiene agregado el contacto.
    # Si no lo tiene agregado arroja un error.
    try:
        contacto = Contactos.objects.get(usuario=user, contacto=contact)
    except Contactos.DoesNotExist:
        return Response({"error":True, "error_cause":"Contact not found!"}, status=status.HTTP_404_NOT_FOUND)

    # Determinamos si el usuario tiene un evento asociado
    """
    Un usuario está asociado a un evento si:
    - El usuario no ha creado algún evento.
    - El usuario no ha sido agregado a alguna actividad de un evento.
    """
    # consultamos la tabla "Evento", para ver si el contacto creó un evento.
    try:
        evento = Evento.objects.get(id_usuario=contact)
        return Response({"error":True, "error_cause":"Contact is associated with an event; event: '{nombre_evento}'".format(nombre_evento=evento.nombre)}, status=status.HTTP_400_BAD_REQUEST)
    except Evento.DoesNotExist:
        print("El contacto no tiene un evento creado!")

    # consultamos la tabla "ParticipantesEventoActividad", para ver si el contacto
    # ha sido agregado a un evento.
    try:
        participantes_eventos = ParticipantesEventoActividad.objects.get(id_participante=contact)
        return Response({"error":True, "error_cause":"Contact is associated with an event's activity; activity: '{nombre_actividad}', evento: '{nombre_evento}'".format(nombre_actividad=participantes_eventos.id_actividad.descripcion, nombre_evento=participantes_eventos.id_evento.nombre)}, status=status.HTTP_400_BAD_REQUEST)
    except ParticipantesEventoActividad.DoesNotExist:
        print("El contacto no está agregado a alguna actividad de un evento!")
    
    # Finalmente, si pasa todas las pruebas, se elimina el contacto.
    contacto.delete()
    return Response({"error":False, "message":"User-contact deleted successfully!"}, status=status.HTTP_200_OK)

# Listar contactos de un usuario especifico

@api_view(['POST'])
def listar_contactos(request):
    # Determinamos si el usuario existe
    try:
        user = User.objects.get(email=request.data["email"])
    except User.DoesNotExist:
        return Response({"error":True, "error_cause":"User does not exist!"}, status=status.HTTP_404_NOT_FOUND)

    # Buscamos los eventos creados por el usuario
    try:
        contactos = Contactos.objects.filter(usuario=user) 
    except Contactos.DoesNotExist:
        return Response({ "contactos" : [], "message": "User hasn't contacts yet"  }, status=status.HTTP_200_OK)
    
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
        return Response({"error":True, "error_cause":"User does not exist!"}, status=status.HTTP_404_NOT_FOUND)

    # Buscamos los eventos creados por el usuario
    try:
        eventos = Evento.objects.filter(id_usuario=user) 
    except Evento.DoesNotExist:
        return Response({ "contactos" : [], "message": "User hasn't created events yet!"  }, status=status.HTTP_200_OK)
    
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
# Gestión de eventos
# --------------------------------------------------------------------------------

# Vista para ver eventos en los que el usuario participa, las actividades registradas en dichos eventos.

@api_view(['GET']) # Es un decorador que me sirve para renderizar en pantalla la vista basada en función.
@authentication_classes([TokenAuthentication]) # Me sirve para permitir autenticación por token para acceder a este método.
@permission_classes([IsAuthenticated])
def ver_eventos_actividades_usuario(request):
    if request.method == 'GET':
        # Obtenemos al usuario por medio de su token
        try:
            user = Token.objects.get(key=request.auth.key).user
        except Token.DoesNotExist:
            return Response({"error": True, "error_cause": 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        # Buscamos los eventos creados por el usuario
        try:
            eventos_creados = Evento.objects.filter(id_usuario=user) 
        except Evento.DoesNotExist:
            print("User hasn't created events yet!")
        
        # Variable auxiliar para guardar todas las actividades en las que el usuario participa.
        lista_eventos_actividades = []

        # Variable auxiliar para almacenar todos los eventos creados por el usuario
        lista_eventos_creados = []

        # Ahora guardamos los eventos que fueron creados por el mismo.
        for evento in eventos_creados:
            # Averiguamos cuales son las actividades asignadas para dicho evento
            # Validamos si tiene actividades asociadas. 
            # si no tiene se deja un espacio vacío
            try:
                evento_actividades = ParticipantesEventoActividad.objects.filter(id_evento=evento) 
                print("evento_actividades:", evento_actividades)
                if len(evento_actividades) > 0:
                    for event_act in evento_actividades:
                        evento_actividad = {
                            "evento": event_act.id_evento.nombre,
                            "actividad": event_act.id_actividad.descripcion,
                        }
                else:
                    # En caso de que no hayan actividades asociadas al evento, se deja un string vacío
                    evento_actividad = {
                        "evento": evento.nombre,
                        "actividad": "",
                    }

                lista_eventos_creados.append(evento_actividad)
            except Evento.DoesNotExist:
                print(f"This event hasn't activities assigned yet: {evento.nombre}")
        
        # Buscamos los eventos en los que participa el usuario.
        try:
            eventos_participante = ParticipantesEventoActividad.objects.filter(id_participante=user) 
        except Evento.DoesNotExist:
            print("User isn't participant of events yet!")

        # Ahora guardamos los eventos en los que el usuario participa.
        for evento in eventos_participante:
            evento_actividad = {
                "evento": evento.id_evento.nombre,
                "actividad": evento.id_actividad.descripcion,
            }
            lista_eventos_actividades.append(evento_actividad)
            
        # Se valida si el usuario participa en algún evento o creó uno.
        if len(lista_eventos_actividades) > 0 or  len(lista_eventos_creados) > 0:
            eventos_actividades_data = { "eventos_creados": lista_eventos_creados, "actividades_en_que_participa": lista_eventos_actividades, "message": "Ok!" }
            return Response(eventos_actividades_data, status=status.HTTP_200_OK)
        else:
            return Response({"error": True, "error_cause": "User isn't participant of any event yet!"}, status=status.HTTP_404_NOT_FOUND) 
    else:
        return Response({"error": True, "error_cause": 'Invalid request method!'}, status=status.HTTP_400_BAD_REQUEST) 

# Vista para ver actividades de un evento.
@api_view(['GET']) # Es un decorador que me sirve para renderizar en pantalla la vista basada en función.
@authentication_classes([TokenAuthentication]) # Me sirve para permitir autenticación por token para acceder a este método.
@permission_classes([IsAuthenticated])
def ver_actividades_evento(request):
    if request.method == 'GET':
        # Obtenemos al usuario por medio de su token
        try:
            user = Token.objects.get(key=request.auth.key).user
        except Token.DoesNotExist:
            return Response({"error": True, "error_cause": 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Consultamos el evento a partir de su nombre
        try:
            evento = Evento.objects.get(nombre=request.data["nombre"])
        except Evento.DoesNotExist:
            return Response({"error": True, "error_cause": "User hasn't created this event {event}".format(event=request.data["nombre"])}, status=status.HTTP_404_NOT_FOUND)
        
        # Miramos cuales actividades están asociadas al evento.
        try:
            actividades = Actividades.objects.filter(id_evento=evento)
        except Actividades.DoesNotExist:
            return Response({"error": True, "error_cause": "Activity doens't exist!"}, status=status.HTTP_404_NOT_FOUND)

        # Variable para guardar actividades
        lista_actividades = []

        # Guardamos cada actividad en la lista
        for actividad in actividades:
            activity = {
                "actividad_descripcion": actividad.descripcion,
                "actividad_valor": actividad.valor,
                "evento": actividad.id_evento.nombre,
            }
            lista_actividades.append(activity)

        return Response({"error": False, "actividades": lista_actividades, "message": "Ok!"}, status=status.HTTP_200_OK)

# Vista para ver los saldos pendientes del usuario

@api_view(['GET']) # Es un decorador que me sirve para renderizar en pantalla la vista basada en función.
@authentication_classes([TokenAuthentication]) # Me sirve para permitir autenticación por token para acceder a este método.
@permission_classes([IsAuthenticated])
def ver_saldos_pendientes(request):
    if request.method == 'GET':
        # Obtenemos al usuario por medio de su token
        try:
            user = Token.objects.get(key=request.auth.key).user
        except Token.DoesNotExist:
            return Response({"error": True, "error_cause": 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        # Buscamos los eventos en los que participa el usuario
        try:
            eventos_participante = ParticipantesEventoActividad.objects.filter(id_participante=user) 
        except Evento.DoesNotExist:
            print("User isn't participant of events yet!")

        # Variable auxiliar para guardar todas las actividades en las que el usuario participa.
        lista_eventos_actividades = []

        # Ahora guardamos las actividades en las que el usuario participa, junto con su saldo pendiente.
        for evento in eventos_participante:
            evento_actividad = {
                "evento": evento.id_evento.nombre,
                "actividad": evento.id_actividad.descripcion,
                "saldo_pendiente": evento.valor_participacion,
            }
            lista_eventos_actividades.append(evento_actividad)

        # Se valida si el usuario participa en algún evento o creó uno.
        if len(lista_eventos_actividades) > 0:
            eventos_actividades_data = { "eventos_actividades": lista_eventos_actividades, "message": "Ok!" }
            return Response(eventos_actividades_data, status=status.HTTP_200_OK)
        else:
            return Response({"error": True, "error_cause": "User isn't participant of any event yet!"}, status=status.HTTP_404_NOT_FOUND) 
    else:
        return Response({"error": True, "error_cause": 'Invalid request method!'}, status=status.HTTP_400_BAD_REQUEST) 

# Vista para modificar los datos de un evento (solo puede el creador) si no tiene actividades asociadas.

@api_view(['PUT']) # Es un decorador que me sirve para renderizar en pantalla la vista basada en función.
@authentication_classes([TokenAuthentication]) # Me sirve para permitir autenticación por token para acceder a este método.
@permission_classes([IsAuthenticated])
def modificar_evento(request):
    if request.method == 'PUT':
        # Obtenemos al usuario por medio de su token
        try:
            user = Token.objects.get(key=request.auth.key).user
        except Token.DoesNotExist:
            return Response({"error": True, "error_cause": 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        # Buscamos el evento que queremos modificar por medio del usuario y el nombre del evento (el cual es único).
        try:
            evento = Evento.objects.get(id_usuario=user, nombre=request.data["nombre"])
        except Evento.DoesNotExist:
            return Response({"error": True, "error_cause": "User hasn't created this event {event}".format(event=request.data["nombre"])}, status=status.HTTP_404_NOT_FOUND)
        
        request.data["id_usuario"] = user.id

        # Actualizamos los datos del evento con el serializador del mismo
        serializer = EventoSerializer(evento, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error":True, "error_cause":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# --------------------------------------------------------------------------------
# Gestión de actividades
# --------------------------------------------------------------------------------

# Vista para crear actividades y agregarlas a un evento.

@api_view(['POST']) # Es un decorador que me sirve para renderizar en pantalla la vista basada en función.
@authentication_classes([TokenAuthentication]) # Me sirve para permitir autenticación por token para acceder a este método.
@permission_classes([IsAuthenticated])
def crear_actividad(request):
    if request.method == 'POST':
        # Obtenemos al usuario por medio de su token
        try:
            user = Token.objects.get(key=request.auth.key).user
        except Token.DoesNotExist:
            return Response({"error": True, "error_cause": 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        # Buscamos el evento al que queremos asociar dicha actividad
        try:
            evento = Evento.objects.get(id_usuario=user, nombre=request.data["nombre_evento"])
        except Evento.DoesNotExist:
            return Response({"error": True, "error_cause": "User hasn't created this event {event}".format(event=request.data["nombre"])}, status=status.HTTP_404_NOT_FOUND)

        # Creamos la actividad.
        activity = Actividades.objects.create(
            descripcion = request.data["descripcion"],
            valor = request.data["valor"],
            id_evento = evento,
        )
        activity.save()
        serializer = ActividadesSerializer(activity, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Vista para quitar actividades de un evento.
@api_view(['POST']) # Es un decorador que me sirve para renderizar en pantalla la vista basada en función.
@authentication_classes([TokenAuthentication]) # Me sirve para permitir autenticación por token para acceder a este método.
@permission_classes([IsAuthenticated])
def quitar_actividad(request):
    if request.method == 'POST':
        # Obtenemos al usuario por medio de su token
        try:
            user = Token.objects.get(key=request.auth.key).user
        except Token.DoesNotExist:
            return Response({"error": True, "error_cause": 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        # Buscamos la actividad por su descripción (es única)
        try:
            actividad = Actividades.objects.get(descripcion=request.data["descripcion"])
        except Actividades.DoesNotExist:
            return Response({"error": True, "error_cause": 'Activity does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validamos que el usuario sea el dueño del evento, al que está vinculada la actividad.
        try:
            evento = Evento.objects.get(nombre=actividad.id_evento.nombre, id_usuario=user)
        except Evento.DoesNotExist:
            return Response({"error": True, "error_cause": 'Event does not exist or User is not its current owner!'}, status=status.HTTP_400_BAD_REQUEST)

        actividad.delete()
        return Response({"error": False, "message": 'Activity deleted successfully!'}, status=status.HTTP_200_OK)

# Vista para realizar pagos de actividades.

# Vista para que un usuario elimine o modifique actividades en un evento creado.

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