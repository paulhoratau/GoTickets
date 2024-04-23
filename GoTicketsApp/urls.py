from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name="index"),

    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logoutUser, name="logout"),

    path('event/create/', views.eventcreate, name='eventcreate'),
    path('events/', views.events, name='events'),
    path('events/<int:id>/', views.events_by_id, name="events_by_id"),
    path('events/<int:id>/manage/', views.event_manage, name="event_manage"),

    path('cart/', views.cart_detail, name='cart_detail'),
    path('add/<int:event_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order/confirmation', views.order_confirmation, name='order_confirmation'),
]
