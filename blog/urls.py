from django.urls import path

from . import views

urlpatterns = [
    path('sermon/<int:pk>', views.index, name='index'),
    path('tuwen/<int:pk>', views.tuwen, name='tuwen'),

]