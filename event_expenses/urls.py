from django.urls import path, include
from rest_framework import routers
from event_expenses import views

#api versioning
router = routers.DefaultRouter()

router.register(r'usuario', views.UsuarioViews, 'usuario' )
router.register(r'contactos', views.ContactoViews, 'contactos' )
router.register(r'actividades', views.ActividadesViews, 'actividades' )
router.register(r'evento', views.EventoViews, 'evento' )
router.register(r'participantesEventoActividad', views.ParticipantesViews, 'participantes' )
   
#Generando rutas CRUD
#Ruta ejemplo= http://localhost:8000/event_expenses/api/v1/usuario
urlpatterns = [
    path("api/v1/", include(router.urls)),
]