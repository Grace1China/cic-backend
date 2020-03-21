from django.urls import path

from . import views

urlpatterns = [
    path('sermon/<int:pk>', views.index, name='index'),
]