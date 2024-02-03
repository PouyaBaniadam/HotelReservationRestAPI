from django.contrib import admin

from reservation.models import Room, UserReservationHistory, RoomHistory

admin.site.register(Room)
admin.site.register(UserReservationHistory)
admin.site.register(RoomHistory)
