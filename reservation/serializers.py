from rest_framework import serializers

from reservation.models import Room, UserReservationHistory


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class UserReservationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReservationHistory
        fields = '__all__'
