from django.urls import path, include, re_path
from rest_framework import routers
from event_expenses import views

# ================================================================================
# api versioning
# ================================================================================

# --------------------------------------------------------------------------------
# Crear y ver instancias de los modelos
# --------------------------------------------------------------------------------
router = routers.DefaultRouter()

router.register(r'contactos', views.ContactoViews, 'contactos' )
router.register(r'actividades', views.ActividadesViews, 'actividades' )
router.register(r'evento', views.EventoViews, 'evento' )
router.register(r'participantesEventoActividad', views.ParticipantesViews, 'participantes' )

# --------------------------------------------------------------------------------   
# Generando rutas
# --------------------------------------------------------------------------------
# Ruta ejemplo= http://localhost:8000/event_expenses/api/v1/usuario
# *** PARA VER MAS EJEMPLOS CONSULTAR EL ARCHIVO urls_ejemplos.txt ***
# --------------------------------------------------------------------------------

urlpatterns = [
    path("api/v1/", include(router.urls)),
    re_path("test_token", views.TestToken),
    re_path("usuario/login", views.UsuarioLoginViews),
    re_path("usuario/registrar", views.UsuarioSingUpViews)
]