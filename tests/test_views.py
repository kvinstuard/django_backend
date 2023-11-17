from event_expenses.models import Usuario, User, Contactos, Evento, Actividades, ParticipantesEventoActividad
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
import pytest
import json

# ----------------------------------------------------------------------
# Pruebas unitarias de Views:
# ----------------------------------------------------------------------

@pytest.fixture
def api_client():
    return APIClient()


#Pruebas usuario

@pytest.mark.django_db
def test_crear_usuario():
    client = APIClient()

    #Se definen los datos del usuario que se quiere enviar en la solicitud POST
    data = {
        "email": "test@example.com",
        "nombres": "Usuario",
        "apellidos": "Prueba",
        "password": "contrasena",
        "apodo": "usuario_prueba",
        "foto": "ruta/a/la/foto.jpg"
    }

    # Realiza una solicitud POST a la vista de crear_usuario
    response = client.post(reverse('crear_usuario'), data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert Usuario.objects.filter(user__email=data['email']).exists()


@pytest.mark.django_db
def test_modificar_usuario(api_client):
    user = User.objects.create_user(username = 'pruebaa', email="test@example.com", password="password123")
    url = reverse('modificar_usuario')
    data = {
        "email": "test@example.com",
        "nombres": "Updated Test",
        "apellidos": "Updated User",
        "password": "newpassword123",
        "apodo": "updateduser",
        "foto": "updated_test.jpg",
        "is_active": "True"
    }
    response = api_client.put(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_login_user(api_client):
    client = APIClient()
    user = User.objects.create_user(username= 'pruebaman', email="test@example.com", password="password123")
    token, created = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    url = reverse('login_user')
    data = {
        "email": user.email,
        "password": "password123",
        'key': 'value'
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK



@pytest.mark.django_db
def test_listar_usuarios():
    client = APIClient()
    url = reverse('crear_usuario') 
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

#Pruebas contactos

@pytest.mark.django_db
def test_agregar_contacto():
    client = APIClient()
    user = User.objects.create(username='exam', email='user@example.com')
    contact = User.objects.create(username='exam2',email='contact@example.com')
    data = {
        'correo_usuario': user.email,
        'correo_contacto': contact.email
    }
    url = reverse('agregar_contacto') 
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_eliminar_contacto():
    client = APIClient()
    user = User.objects.create(username='exam', email='user@example.com')
    contact = User.objects.create(username='exam2',email='contact@example.com')
    contacto = Contactos.objects.create(usuario=user, contacto=contact)
    data = {
        'correo_usuario': user.email,
        'correo_contacto': contact.email
    }
    url = reverse('eliminar_contacto')
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_listar_contactos(api_client):
    user = User.objects.create_user(username='example', email="user1@example.com", password="password123")
    contact = User.objects.create_user(username='example2', email="user2@example.com", password="password123")
    Contactos.objects.create(usuario=user, contacto=contact)
    url = reverse('listar_contactos')
    data = {
        "email": "user1@example.com"
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_listar_contactos_evento(api_client):
    user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
    # Crear un evento asociado al usuario
    evento = Evento.objects.create(
        nombre='Evento de prueba',
        tipo='VIAJE',
        foto='ruta/a/la/foto.jpg',
        id_usuario=user
    )

    # Crear una actividad asociada al usuario y al evento
    actividad = Actividades.objects.create(
        descripcion='Actividad de prueba',
        valor=50.0,
        id_evento=evento,
        id_usuario=user
    )

    # Crear un evento_actividad asociado a la actividad y usuario
    evento_actividad = ParticipantesEventoActividad.objects.create(
        id_actividad=actividad,
        id_evento=evento,
        id_participante=user,
        valor_participacion=30
    )

    # Simular una solicitud POST a la vista listar_contactos_evento
    url = reverse('listar_contactos_evento')
    data = {"email": user.email}
    response = api_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    response_data = json.loads(response.content)

    assert "contactos" in response_data
    assert len(response_data["contactos"]) == 1

    contacto = response_data["contactos"][0]
    assert contacto["email"] == user.email
    assert contacto["nombre_usuario"] == user.username
    assert contacto["evento"] == evento.nombre
    assert contacto["actividad"] == actividad.descripcion
    
@pytest.mark.django_db
def test_listar_saldos_pendientes_contactos(api_client):
    # Crear usuarios y tokens para la autenticación
    user1 = User.objects.create_user(username='user1', email='user1@example.com', password='password1')
    user2 = User.objects.create_user(username='user2', email='user2@example.com', password='password2')

    token1, _ = Token.objects.get_or_create(user=user1)
    token2, _ = Token.objects.get_or_create(user=user2)

    # Crear contactos
    contacto_user1 = Contactos.objects.create(usuario=user1, contacto=user2)
    contacto_user2 = Contactos.objects.create(usuario=user2, contacto=user1)

    # Crear eventos, actividades y participaciones
    evento_user1 = Evento.objects.create(nombre='Evento 1', tipo='VIAJE', foto='foto1.jpg', id_usuario=user1)
    evento_user2 = Evento.objects.create(nombre='Evento 2', tipo='HOGAR', foto='foto2.jpg', id_usuario=user2)

    actividad_user1 = Actividades.objects.create(descripcion='Actividad 1', valor=30.0, id_evento=evento_user1, id_usuario=user1)
    actividad_user2 = Actividades.objects.create(descripcion='Actividad 2', valor=40.0, id_evento=evento_user2, id_usuario=user2)

    participacion_user1 = ParticipantesEventoActividad.objects.create(
        id_actividad=actividad_user1,
        id_evento=evento_user1,
        id_participante=user2,
        valor_participacion=20.0,
        valor_pagado=10.0,
        aceptado=True
    )

    # Simular una solicitud GET a la vista listar_saldos_pendientes_contactos
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token1.key)
    url = reverse('listar_saldos_pendientes_contactos')
    response = api_client.get(url)


    assert response.status_code == status.HTTP_200_OK
    response_data = json.loads(response.content)

    assert "eventos_actividades" in response_data
    assert len(response_data["eventos_actividades"]) == 1

    evento_actividad = response_data["eventos_actividades"][0]
    assert evento_actividad["contacto"] == user2.username
    assert evento_actividad["evento"] == evento_user1.nombre
    assert evento_actividad["saldo_pendiente"] == 10.0
    assert evento_actividad["saldo_total"] == 20.0
    assert response_data["message"] == "Ok!"


#Pruebas eventos
@pytest.mark.django_db
def test_ver_eventos_actividades_usuario(api_client):
    # Crear usuarios y tokens para la autenticación
    user1 = User.objects.create_user(username='user1', email='user1@example.com', password='password1')
    token1, _ = Token.objects.get_or_create(user=user1)
    
    # Crear eventos, actividades y participaciones
    evento_user1 = Evento.objects.create(nombre='Evento 1', tipo='VIAJE', foto='foto1.jpg', id_usuario=user1)
    actividad_user1 = Actividades.objects.create(descripcion='Actividad 1', valor=30.0, id_evento=evento_user1, id_usuario=user1)
   
    participacion_user1 = ParticipantesEventoActividad.objects.create(
        id_actividad=actividad_user1,
        id_evento=evento_user1,
        id_participante=user1,
        valor_participacion=20.0,
        valor_pagado=10.0,
        aceptado=True
    )


    # Simular una solicitud GET a la vista ver_eventos_actividades_usuario
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token1.key)
    url = reverse('ver_eventos_actividades_usuario')
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    response_data = json.loads(response.content)

    # Verificar que los datos esperados están presentes en la respuesta
    assert "eventos_creados" in response_data
    assert "actividades_en_que_participa" in response_data

    evento_creado = response_data["eventos_creados"][0]
    assert evento_creado["evento"] == evento_user1.nombre
    assert evento_creado["evento_tipo"] == evento_user1.tipo

    actividad_participante = response_data["actividades_en_que_participa"][0]
    assert actividad_participante["evento"] == evento_user1.nombre
    assert actividad_participante["evento_tipo"] == evento_user1.tipo
    assert actividad_participante["actividad"] == actividad_user1.descripcion

    assert response_data["message"] == "Ok!"

#Fallo
@pytest.fixture
@pytest.mark.django_db
def setup_events_and_activities():
    user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
    token, _ = Token.objects.get_or_create(user=user)

    evento_1 = Evento.objects.create(
        nombre='Evento 1',
        tipo='VIAJE',
        foto='ruta/a/la/foto1.jpg',
        id_usuario=user
    )

    actividad_1 = Actividades.objects.create(
        descripcion='Actividad 1',
        valor=20.0,
        id_evento=evento_1,
        id_usuario=user
    )

    evento_2 = Evento.objects.create(
        nombre='Evento 2',
        tipo='VIAJE',
        foto='ruta/a/la/foto2.jpg',
        id_usuario=user
    )

    actividad_2 = Actividades.objects.create(
        descripcion='Actividad 2',
        valor=30.0,
        id_evento=evento_2,
        id_usuario=user
    )

    return evento_1, evento_2, actividad_1, actividad_2, token

@pytest.mark.django_db
def test_ver_saldos_pendientes_failure(setup_events_and_activities):
    evento_1, evento_2, actividad_1, actividad_2, token = setup_events_and_activities

    api_client = APIClient()
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    # Realizar la solicitud GET a la vista
    url = reverse('ver_saldos_pendientes')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND

#####

@pytest.mark.django_db
def test_modificar_evento_success():
    user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
    token, _ = Token.objects.get_or_create(user=user)
    evento = Evento.objects.create(
        nombre='Evento de prueba',
        tipo='TIPO',
        foto='ruta/a/la/foto.jpg',
        id_usuario=user
    )

    # Crear un cliente de prueba
    client = APIClient()

    # Autenticar el cliente con el token
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    url = reverse('modificar_evento')
    data = {
        "nombre_antiguo": evento.nombre,
        "nombre": "Nuevo nombre",
        "tipo": "VIAJE",
        "foto": "nueva/ruta/a/la/nueva/foto.jpg",
    }

    response = client.put(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_modificar_evento_failure():
    user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
    token, _ = Token.objects.get_or_create(user=user)
    evento = Evento.objects.create(
        nombre='Evento de prueba',
        tipo='TIPO',
        foto='ruta/a/la/foto.jpg',
        id_usuario=user
    )

    # Crear un cliente de prueba
    client = APIClient()

    # Autenticar el cliente con el token
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    url = reverse('modificar_evento')
    data = {
        "nombre_antiguo": evento.nombre,
        "nombre": "Nuevo nombre",
        "tipo": "RUMBAAA",
        "foto": "nueva/ruta/a/la/nueva/foto.jpg",
    }

    response = client.put(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

