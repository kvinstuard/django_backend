from event_expenses.models import Usuario
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
import pytest

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
def test_listar_usuarios():
    client = APIClient()
    url = reverse('crear_usuario') 
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

