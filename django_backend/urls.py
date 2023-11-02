"""
URL configuration for django_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from event_expenses import views

# ================================================================================
#Enseñandole al proyecto la ruta de las urls
# ================================================================================
# --------------------------------------------------------------------------------
# Ruta ejemplo= http://localhost:8000/event_expenses/api/v1/usuario
# *** PARA VER MAS EJEMPLOS CONSULTAR EL ARCHIVO urls_ejemplos.txt ***
# --------------------------------------------------------------------------------

urlpatterns = [
    path('admin/', 
         admin.site.urls),
    path('event_expenses/', 
         include('event_expenses.urls')),
    path('crear/usuario/', 
         views.crear_usuario, name="crear_usuario"),
    path("agregar/contacto/", 
         views.agregar_contacto, name="agregar_contacto"),
    path("eliminar/contacto/", 
         views.eliminar_contacto, name="eliminar_contacto"),
    path('login/user/', 
         views.login_user, name="login_user"),
]
