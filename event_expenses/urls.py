from django.urls import path, include
from rest_framework import routers
from event_expenses import views

# ================================================================================
# api versioning
# ================================================================================

# --------------------------------------------------------------------------------
# Crear y ver instancias de los modelos
# --------------------------------------------------------------------------------
router = routers.DefaultRouter()

router.register(r'usuario', views.UsuarioViews, 'usuario' )
router.register(r'contactos', views.ContactoViews, 'contactos' )
router.register(r'actividades', views.ActividadesViews, 'actividades' )
router.register(r'evento', views.EventoViews, 'evento' )
router.register(r'participantesEventoActividad', views.ParticipantesViews, 'participantes' )

# --------------------------------------------------------------------------------
# Gestión de contactos
# --------------------------------------------------------------------------------
gestion_contactos = routers.DefaultRouter()
router.register(r'crear/contacto', views.agregar_contacto, 'crear/contacto')

# --------------------------------------------------------------------------------   
# Generando rutas
# --------------------------------------------------------------------------------
# Ruta ejemplo= http://localhost:8000/event_expenses/api/v1/usuario
# *** PARA VER MAS EJEMPLOS CONSULTAR EL ARCHIVO urls_ejemplos.txt ***
# --------------------------------------------------------------------------------

urlpatterns = [
    path("api/v1/", include(router.urls)),
    path("/gestion_contactos/", include(gestion_contactos.urls)),
    # path("/create/contact"),
]