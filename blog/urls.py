from django.urls import path

from . import views

urlpatterns = [
    path('sermon/<int:pk>', views.index, name='index'),
    path('tuwen/<int:pk>', views.tuwen, name='tuwen'),
    path('media/<int:pk>', views.media, name='media'),
    path('ccol/<int:pk>', views.column_content_medias, name='ccol'),



]