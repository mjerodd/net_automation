from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('core-temp/', views.core_temp, name='core-template'),
    path('thanks/', views.thank_you, name='thank-you'),
    path('int-descriptions/', views.int_descriptions, name='int-descriptions'),
]