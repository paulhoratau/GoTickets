from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from .views import eventcreate

urlpatterns = [
    path('', views.index, name="index"),

    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logoutUser, name="logout"),


    path('event/create/', views.eventcreate, name='eventcreate'),
    path('events/', views.events, name='events'),
    path('events/<int:id>/', views.events_by_id, name="events_by_id"),
    path('events/<int:id>/manage/', views.event_manage, name="event_manage"),
    path('events/<int:id>/ticket_confirmation', views.ticket_confirmation, name="ticket_confirmation"),
    path('events/<int:event_id>/qr/', views.generate_ticket_qr, name='event_qr'),
    path('confirm_post/xml', views.confirm_post, name="confirm_post"),


    path('order/confirmation', views.order_confirmation, name='order_confirmation'),
    path('checkout/', views.checkout, name='checkout'),

    path('account/', views.account, name="account"),
    path('account/user_tickets/', views.user_tickets, name="user_tickets"),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
