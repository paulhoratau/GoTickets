from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name="index"),

    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logoutUser, name="logout" ),

    path('event/create/', views.eventcreate, name='eventcreate'),
    path('events', views.events, name='events'),

]
