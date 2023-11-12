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
from django.db.models import Sum
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from django.db.models.signals import post_save
from django.core import serializers
import json
import random
from decimal import Decimal

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
            password = make_password(request.data["password"]),
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
        user = User.objects.get(email=request.data["email"])
    except User.DoesNotExist:
        return Response({"error": True, "error_cause": 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    # Verificar la contraseña utilizando check_password
    if not check_password(request.data["password"], user.password):
        return Response({"error": True, "error_cause": 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)

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
                "email": eventoActividad.id_participante.email,
                "nombre": eventoActividad.id_participante.first_name,
                "evento": eventoActividad.id_evento.nombre,
                "actividad": eventoActividad.id_actividad.descripcion,
                "saldo": eventoActividad.valor_participacion - eventoActividad.valor_pagado,
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
                "saldo_pendiente": evento.valor_participacion - evento.valor_pagado,
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
# Restricciones: 
# - Solo el creador puede modificar un evento.
# - Solo se puede modificar el evento si no tiene actividades asociadas. 

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
            evento = Evento.objects.get(id_usuario=user, nombre=request.data["nombre_antiguo"])
        except Evento.DoesNotExist:
            return Response({"error": True, "error_cause": "User hasn't created this event {event}".format(event=request.data["nombre_antiguo"])}, status=status.HTTP_404_NOT_FOUND)
        
        # Validamos que el evento no tenga actividades asociadas
        try:
            actividades = Actividades.objects.get(id_evento=evento)
            return Response({"error": True, "error_cause": "There's one activity: {act}, in this event: {event}".format(act=actividades.descripcion,event=evento.nombre)}, status=status.HTTP_404_NOT_FOUND)
        except Actividades.DoesNotExist:
            print("There're no activities in this event!, we can continue...")

        request.data["id_usuario"] = user.id

        # Actualizamos los datos del evento con el serializador del mismo
        serializer = EventoSerializer(evento, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error":True, "error_cause":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# Vista para realizar pagos de actividades (en los eventos).
# Recordar: 
# - los pagos pueden ser parciales
# - el creador (prestador) o contacto (deudor) pueden registrar el pago.
# - los pagos se hacen por evento, cuando se calculan las diferencias, no por actividad.
@api_view(['POST']) # Es un decorador que me sirve para renderizar en pantalla la vista basada en función.
@authentication_classes([TokenAuthentication]) # Me sirve para permitir autenticación por token para acceder a este método.
@permission_classes([IsAuthenticated])
def pagar_actividad_evento(request):
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
            return Response({"error": True, "error_cause": 'Activity not found!'}, status=status.HTTP_404_NOT_FOUND)
        
        # Buscamos por medio de la actividad, el valor de participación a pagar.
        try:
            # Primero validemos si es participante (deudor)
            eventosActividades = ParticipantesEventoActividad.objects.get(id_actividad=actividad, id_participante=user)
        except ParticipantesEventoActividad.DoesNotExist:
            # En caso de que no sea participante (deudor), averiguemos si es el creador (prestador)
            try:
                evento = Evento.objects.get(nombre=actividad.id_evento.nombre, id_usuario=user)
            except Evento.DoesNotExist:
                return Response({"error": True, "error_cause": "User cannot pay the bill, due to it isn't neither the owner nor participant!"}, status=status.HTTP_400_BAD_REQUEST)
            # Si es el dueño de la actividad y va a realizar el pago, entonces debemos obtener 
            # obligatoriamente los datos de "ParticipantesEventoActividad", para pagar sobre 
            # el valor de la participación.
            try:
                eventosActividades = ParticipantesEventoActividad.objects.get(id_actividad=actividad, id_evento=evento)
            except ParticipantesEventoActividad.DoesNotExist:
                return Response({"error": True, "error_cause": "User cannot pay the bill, due to it isn't neither the owner nor participant!"}, status=status.HTTP_400_BAD_REQUEST)

        # Ahora pagamos la actividad
        # El sistema automaticamente asigna el valor de participacion como valor pagado si el pago 
        # excede el valor de participación o ya pagó la deuda.
        valor_a_pagar = request.data["valor_a_pagar"]
        
        # si el valor es negativo, retorna error
        if valor_a_pagar < 0:
            return Response({"error": True, "error_cause": "Value to pay must be a positive value!"}, status=status.HTTP_400_BAD_REQUEST)
        
        if eventosActividades.valor_pagado == eventosActividades.valor_participacion:
            return Response({"error": True, "error_cause": "Bill has been paid!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if valor_a_pagar > eventosActividades.valor_participacion or (valor_a_pagar + eventosActividades.valor_pagado) >= eventosActividades.valor_participacion:
                eventosActividades.valor_pagado = eventosActividades.valor_participacion
            else:
                eventosActividades.valor_pagado += valor_a_pagar
        eventosActividades.save()
        serializer = ParticipantesSerializer(eventosActividades, many=False)
        return Response({"error": False, "description": serializer.data, "error_cause": "Payment made successfully!"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": True, "error_cause": 'Invalid request method!'}, status=status.HTTP_400_BAD_REQUEST) 


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
            return Response({"error": True, "error_cause": 'Event associated with activity, does not exist or User is not its current owner!'}, status=status.HTTP_400_BAD_REQUEST)

        actividad.delete()
        return Response({"error": False, "message": 'Activity deleted successfully!'}, status=status.HTTP_200_OK)

# Vista para ver actividades de un evento.

@api_view(['POST']) # Es un decorador que me sirve para renderizar en pantalla la vista basada en función.
@authentication_classes([TokenAuthentication]) # Me sirve para permitir autenticación por token para acceder a este método.
@permission_classes([IsAuthenticated])
def ver_actividades_evento(request):
    if request.method == 'POST':
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

# Vista para que un usuario elimine o modifique actividades en un evento creado.

@api_view(['PUT']) # Es un decorador que me sirve para renderizar en pantalla la vista basada en función.
@authentication_classes([TokenAuthentication]) # Me sirve para permitir autenticación por token para acceder a este método.
@permission_classes([IsAuthenticated])
def modificar_actividad(request):
    if request.method == 'PUT':
        # Obtenemos al usuario por medio de su token
        try:
            user = Token.objects.get(key=request.auth.key).user
        except Token.DoesNotExist:
            return Response({"error": True, "error_cause": 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Buscamos la actividad a modificar
        try:
            actividad = Actividades.objects.get(descripcion=request.data["antigua_descripcion"])
        except Actividades.DoesNotExist:
            return Response({"error": True, "error_cause": "Activity doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        
        # Validamos que el usuario sea el dueño del evento, al que está vinculada la actividad.
        try:
            evento = Evento.objects.get(nombre=actividad.id_evento.nombre, id_usuario=user)
        except Evento.DoesNotExist:
            return Response({"error": True, "error_cause": 'Event associated with activity, does not exist or User is not its current owner!'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Asignamos el id_evento, porque es obligatorio pasarlo al serializador.
        request.data["id_evento"] = evento.id

        # Modificamos dicha actividad
        serializer = ActividadesSerializer(actividad, data=request.data, many=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error":True, "error_cause":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# Vista para invitar contactos a una actividad de un evento
# Restricciones: 
# - Solo el creador del evento puede agregarlos. 
# - El contacto debe aceptar.
# NOTA: 
# Debido a que el contacto tiene que aceptar, se pondrá por defecto que no aceptó ser participe. 

@api_view(['POST']) # Es un decorador que me sirve para renderizar en pantalla la vista basada en función.
@authentication_classes([TokenAuthentication]) # Me sirve para permitir autenticación por token para acceder a este método.
@permission_classes([IsAuthenticated])
def agregar_contacto_actividad(request):
    if request.method == 'POST':
        # Obtenemos al usuario por medio de su token
        try:
            user = Token.objects.get(key=request.auth.key).user
        except Token.DoesNotExist:
            return Response({"error": True, "error_cause": 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Buscamos la actividad donde queremos asignar al contacto
        try:
            actividad = Actividades.objects.get(descripcion=request.data["descripcion"])
        except Actividades.DoesNotExist:
            return Response({"error": True, "error_cause": "Activity doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        
        # Validamos que el usuario sea el dueño del evento, al que está vinculada la actividad.
        try:
            evento = Evento.objects.get(nombre=actividad.id_evento.nombre, id_usuario=user)
        except Evento.DoesNotExist:
            return Response({"error": True, "error_cause": 'Event associated with activity, does not exist or User is not its current owner!'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Busquemos al contacto que queremos asignar
        try:
            contact = User.objects.get(email=request.data["email_contacto"])
        except User.DoesNotExist:
            return Response({"error":True, "error_cause":"Contact doesn't exist!"}, status=status.HTTP_404_NOT_FOUND)
        
        # Validemos que efectivamente sea contacto del usuario (creador)
        try:
            contacto = Contactos.objects.get(usuario=user, contacto=contact)
        except Contactos.DoesNotExist:
            return Response({"error":True, "error_cause":"User hasn't this contact aggregated yet!"}, status=status.HTTP_404_NOT_FOUND)

        # Miremos si el valor de participación asignado es porcentaje o si es valor númerico 
        # si es porcentaje se calcula su valor númerico equivalente.
        if request.data["valor_participacion"] > 0 and request.data["valor_participacion"] <= 1:
            valor_participacion_contacto = actividad.valor * Decimal(request.data["valor_participacion"])
        else:
            valor_participacion_contacto = request.data["valor_participacion"]

        # Validemos que el valor de participación del contacto no supere el valor total de la actividad
        if valor_participacion_contacto > actividad.valor:
            return Response({"error":True, "error_cause":"Participation's value: {p_val}, is greater than activity's value: {act_val}!".format(
                p_val = valor_participacion_contacto, 
                act_val = actividad.valor, )}, 
            status=status.HTTP_400_BAD_REQUEST)

        # Validemos que la sumatoria del valor de participación y los otros valores de participación no supere el valor de la actividad:
        try:    
            sumatoria_valores_participacion = ParticipantesEventoActividad.objects.filter(id_actividad=actividad, id_evento=evento).aggregate(Sum('valor_participacion', default=0))
            sumatoria_valores_participacion = sumatoria_valores_participacion["valor_participacion__sum"]
        except ParticipantesEventoActividad.DoesNotExist:
            print("This's going to be the first participation!")
        
        if valor_participacion_contacto + sumatoria_valores_participacion > actividad.valor:
            return Response({"error":True, "error_cause":"Sum of participation's values: {p_val}, is greater than activity's value: {act_val}!".format(
                p_val = valor_participacion_contacto + sumatoria_valores_participacion, 
                act_val = actividad.valor, )}, 
            status=status.HTTP_400_BAD_REQUEST)
        
        # Validemos que el contacto no haya sido asignado aún a la actividad
        try:    
            eventosActividades = ParticipantesEventoActividad.objects.get(id_actividad=actividad, id_evento=evento, id_participante=contact)
            return Response({"error":True, "error_cause":"Contact already assigned to this activity!"}, status=status.HTTP_400_BAD_REQUEST)
        except ParticipantesEventoActividad.DoesNotExist:
            print("Contact not assigned yet!")

        # Asignemos el contacto a la actividad
        eventosActividades = ParticipantesEventoActividad.objects.create(
            id_actividad = actividad,
            id_evento = evento,
            id_participante = contact,
            valor_participacion = valor_participacion_contacto
        )
        eventosActividades.save()
        serializer = ParticipantesSerializer(eventosActividades, many=False)

        return Response({"error":False, "description": serializer.data, "sum_valor_participacion": valor_participacion_contacto + sumatoria_valores_participacion}, status=status.HTTP_200_OK)

# Vista para desvincular contacto de una actividad de un evento.
# No tendrá la restriccion de que debe ser el creador quien lo elimine,
# Porque en caso de que no acepte, se eliminará de dicha actividad a la que esté vinculado.
# Restricciones: 
# - Solo el creador del evento puede quitarlos 
# - Se puede quitar el contacto si no se ha registrado alguna actividad diferente a la que está vinculado en el mismo evento.

# NOTA: La vista es para cumplir con el requerimiento: 
# -  Quitar contactos del evento. Solo el creador del evento puede quitarlos y 
# si no se ha registrado alguna actividad.

@api_view(['POST']) # Es un decorador que me sirve para renderizar en pantalla la vista basada en función.
@authentication_classes([TokenAuthentication]) # Me sirve para permitir autenticación por token para acceder a este método.
@permission_classes([IsAuthenticated])
def quitar_contacto_actividad(request):
    # Obtenemos al usuario por medio de su token
    try:
        user = Token.objects.get(key=request.auth.key).user
    except Token.DoesNotExist:
        return Response({"error": True, "error_cause": 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    # Buscamos la actividad donde queremos quitar al contacto
    try:
        actividad = Actividades.objects.get(descripcion=request.data["descripcion"])
    except Actividades.DoesNotExist:
        return Response({"error": True, "error_cause": "Activity doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

    # Validemos que el usuario sea el dueño del evento asociado a esa actividad.
    try:
        evento = Evento.objects.get(nombre=actividad.id_evento.nombre, id_usuario=user)
    except Evento.DoesNotExist:
        return Response({"error": True, "error_cause": 'Event associated with activity, does not exist or User is not its current owner!'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validamos que no hayan actividades diferentes en el mismo evento a la que está vinculado el usuario.
    try:
        actividades_evento = Actividades.objects.filter(id_evento=evento)
        if len(actividades_evento) > 1:
            return Response({"error":True, "error_cause":"There're more activities in the event!"}, status=status.HTTP_400_BAD_REQUEST)
    except Actividades.DoesNotExist:
        print("there're no activities!")

    # Determinamos si el contacto existe.
    try:
        contact = User.objects.get(email=request.data["correo_contacto"])
    except User.DoesNotExist:
        return Response({"error":True, "error_cause":"User-contact not found!"}, status=status.HTTP_404_NOT_FOUND)

    # Validamos que efectivamente el contacto esté asignado a la actividad.
    try:    
        eventosActividades = ParticipantesEventoActividad.objects.get(id_actividad=actividad, id_evento=evento, id_participante=contact)
    except ParticipantesEventoActividad.DoesNotExist:
        return Response({"error":True, "error_cause":"User isn't participant of this activity!"}, status=status.HTTP_400_BAD_REQUEST)

    # Se desvincula al usuario de la actividad
    eventosActividades.delete()
    return Response({"error":False, "message":"User deleted sucessfully from activity!"}, status=status.HTTP_200_OK)

# Vista para aceptar participar de una actividad

@api_view(['POST']) # Es un decorador que me sirve para renderizar en pantalla la vista basada en función.
@authentication_classes([TokenAuthentication]) # Me sirve para permitir autenticación por token para acceder a este método.
@permission_classes([IsAuthenticated])
def aceptar_invitacion_actividad(request):
    # Obtenemos al usuario por medio de su token
    try:
        user = Token.objects.get(key=request.auth.key).user
    except Token.DoesNotExist:
        return Response({"error": True, "error_cause": 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

    # Buscamos la actividad a la que fue invitado por su descripcion
    try:
        actividad = Actividades.objects.get(descripcion=request.data["descripcion"])
    except Actividades.DoesNotExist:
        return Response({"error": True, "error_cause": "Activity doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
    
    # Validamos que efectivamente es participante de esa actividad
    try:
        eventosActividades = ParticipantesEventoActividad.objects.get(id_actividad=actividad, id_participante=user)
    except ParticipantesEventoActividad.DoesNotExist:
        return Response({"error": True, "error_cause": "User cannot accept because isn't participant!"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validamos que el usuario no haya aceptado la actividad
    if eventosActividades.aceptado:
        return Response({"error":True, "error_cause": "User alredy has accepted the activity!"}, status=status.HTTP_200_OK)    
    
    # Aceptamos la invitación
    eventosActividades.aceptado = True
    eventosActividades.save()
    serializer = ParticipantesSerializer(eventosActividades, many=False)

    return Response({"error":False, "description": serializer.data, "message": "Accepted!"}, status=status.HTTP_200_OK)

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