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
    path('event/<int:id>', views.event_by_id, name="event_by_id"),
    path('event/<int:id>/manage/', views.event_manage, name="event_manage"),
    path('event/<int:id>/ticket_detailed/', views.ticket_detailed, name='ticket_detailed'),
    path('event/<int:event_id>/qr/', views.generate_ticket_qr, name='event_qr'),
    path('download-ticket/<int:event_id>/<int:purchase_id>/', views.download_ticket_pdf, name='download_ticket_pdf'),
    path('confirm_post/xml', views.confirm_post, name="confirm_post"),
    path('event/<int:id>/create_ticket', views.create_ticket, name='create_ticket'),

    path('order/confirmation/', views.order_confirmation, name='order_confirmation'),
    path('order/checkout/', views.checkout, name='checkout'),

    path('account/', views.account, name="account"),
    path('account/user_events', views.user_events, name="user_events"),
    path('account/user_events/<str:order_type>/', views.user_events, name='user_events_filtered'),
    path('account/user_tickets/', views.user_tickets, name="user_tickets"),
    path('account/update_account_settings/', views.update_account_settings, name='update_account_settings'),
    path('account/change_password/', views.change_password, name='change_password'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
