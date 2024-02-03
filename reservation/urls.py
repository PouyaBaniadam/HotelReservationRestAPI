from django.urls import path
from .views import RoomListView, MakeReservationView, CheckReservationDates

urlpatterns = [
    path('rooms/', RoomListView.as_view(), name='room-list'),
    path('reserve', MakeReservationView.as_view(), name='room-reserve'),
    path('reservation/check', CheckReservationDates.as_view(), name='check_room-reserve'),
]
