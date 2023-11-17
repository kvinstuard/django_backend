from event_expenses.models import Usuario, User, Contactos, Evento, Actividades, ParticipantesEventoActividad
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
import pytest

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

#@pytest.mark.django_db
#def test_listar_contactos_evento(api_client):
#    user = User.objects.create_user(username='example', email="user1@example.com", password="password123")
#    contact = User.objects.create_user(username='example2',email="user2@example.com", password="password123")
#    evento = Evento.objects.create(id_usuario=user, nombre="Evento de prueba")
#    actividad = Actividades.objects.create(evento=evento, descripcion="Actividad de prueba")
#    participante = ParticipantesEventoActividad.objects.create(id_participante=contact, id_evento=evento, id_actividad=actividad, valor_participacion=50)
#    url = reverse('listar_contactos_evento')
#    data = {
#        "email": "user1@example.com"
#    }
#    response = api_client.post(url, data, format='json')
#    assert response.status_code == status.HTTP_200_OK
