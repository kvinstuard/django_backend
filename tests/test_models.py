import pytest
from django.contrib.auth.models import User
from event_expenses.models import Evento, Usuario, Contactos, Actividades, ParticipantesEventoActividad

@pytest.mark.django_db
def test_crear_evento():
    evento = Evento.objects.create(
        nombre='Evento de prueba',
        tipo='VIAJE',
        foto='ruta/a/la/foto.jpg',
        id_usuario=User.objects.create(username='usuario_prueba')
    )
    assert evento.nombre == 'Evento de prueba'
    assert evento.tipo == 'VIAJE'
    assert evento.id_usuario.username == 'usuario_prueba'


@pytest.mark.django_db
def test_crear_contactos():
    usuario_1 = User.objects.create(username='usuario_1')
    usuario_2 = User.objects.create(username='usuario_2')
    contacto = Contactos.objects.create(usuario=usuario_1, contacto=usuario_2)
    assert contacto.usuario.username == 'usuario_1'
    assert contacto.contacto.username == 'usuario_2'

@pytest.mark.django_db
def test_crear_actividad():
    evento = Evento.objects.create(
        nombre='Evento de prueba',
        tipo='VIAJE',
        foto='ruta/a/la/foto.jpg',
        id_usuario=User.objects.create(username='usuario_prueba')
    )
    actividad = Actividades.objects.create(
        descripcion='Actividad de prueba',
        valor=50.0,
        id_evento=evento
    )
    assert actividad.descripcion == 'Actividad de prueba'
    assert actividad.valor == 50.0

@pytest.mark.django_db
def test_crear_participante_evento_actividad():
    usuario_1 = User.objects.create(username='usuario_1')
    usuario_2 = User.objects.create(username='usuario_2')
    evento = Evento.objects.create(
        nombre='Evento de prueba',
        tipo='VIAJE',
        foto='ruta/a/la/foto.jpg',
        id_usuario=usuario_1
    )
    actividad = Actividades.objects.create(
        descripcion='Actividad de prueba',
        valor=50.0,
        id_evento=evento
    )
    participante = Contactos.objects.create(usuario=usuario_2, contacto=usuario_1)
    participante_evento_actividad = ParticipantesEventoActividad.objects.create(
        id_actividad=actividad,
        id_evento=evento,
        id_participante=participante,
        valor_participacion=30
    )
    assert participante_evento_actividad.id_actividad.descripcion == 'Actividad de prueba'
    assert participante_evento_actividad.valor_participacion == 30
