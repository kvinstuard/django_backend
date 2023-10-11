from django.contrib import admin
from .models import Evento, Usuario, Contactos, Actividades, ParticipantesEventoActividad

# Register your models here.

admin.site.register(Evento)
admin.site.register(Usuario)
admin.site.register(Contactos)
admin.site.register(Actividades)
admin.site.register(ParticipantesEventoActividad)
