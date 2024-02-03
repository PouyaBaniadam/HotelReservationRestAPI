import datetime

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import CustomUser
from .models import Room, RoomHistory, UserReservationHistory
from .serializers import RoomSerializer


class RoomListView(generics.ListAPIView):
    serializer_class = RoomSerializer

    def get_queryset(self):
        queryset = Room.objects.all()

        has_discount_param = self.request.query_params.get('has_discount', None)
        if has_discount_param is not None:
            has_discount = has_discount_param.lower() == 'true'
            queryset = queryset.filter(has_discount=has_discount)

        start_date_param = self.request.query_params.get('start_date', None)
        end_date_param = self.request.query_params.get('end_date', None)

        if start_date_param and end_date_param:
            start_date = datetime.datetime.strptime(start_date_param, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end_date_param, "%Y-%m-%d").date()

            available_rooms = []
            for room in queryset:
                is_available = RoomHistory.objects.filter(room=room, start_date__lte=end_date,
                                                          end_date__gte=start_date).count() == 0

                if is_available:
                    available_rooms.append(room.id)

            queryset = queryset.filter(id__in=available_rooms)

        return queryset


class MakeReservationView(APIView):
    def post(self, request, *args, **kwargs):

        authentication_token = request.data.get('authentication_token', None)
        start_date = request.data.get('start_date', None)
        end_date = request.data.get('end_date', None)
        room_number = request.data.get('room', None)

        user = CustomUser.objects.get(authentication_token=authentication_token)
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
        room = Room.objects.get(number=room_number)

        if end_date < start_date:
            return Response({"message": "End date must be before start date"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            if start_date < timezone.now().date() or end_date < timezone.now().date():
                return Response({"message": "Dates must be in the future"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                room_history = RoomHistory.objects.filter(room=room).values_list("start_date", flat=True)

                if room.is_reserved and start_date in room_history:
                    return Response({'error': 'This room is already reserved for this specified duration.'},
                                    status=status.HTTP_400_BAD_REQUEST)

                else:
                    if not RoomHistory.objects.filter(room=room).exists():
                        room.is_reserved = True
                        room.reserved_by = user
                        days_to_stay = (end_date - start_date).days
                        final_price = days_to_stay * room.price_per_day
                        room.days_to_stay = days_to_stay
                        room.final_price = days_to_stay * room.price_per_day
                        room.start_date = start_date
                        room.end_date = end_date

                        RoomHistory.objects.create(room=room, user=user, start_date=start_date, end_date=end_date,
                                                   final_price=final_price, days_to_stay=days_to_stay)

                        room.save()

                        days_to_stay = (end_date - start_date).days
                        UserReservationHistory.objects.create(user=user, room=room, start_date=start_date,
                                                              end_date=end_date, days=days_to_stay)

                        return Response({'message': 'Room has been reserved successfully.'},
                                        status=status.HTTP_201_CREATED)

                    else:
                        room_history_dates = RoomHistory.objects.filter(room=room).values_list("start_date", flat=True)

                        date_diff = {history_date: abs((timezone.now().date() - history_date).days) for history_date in
                                     room_history_dates}

                        nearest_start_date = min(date_diff, key=date_diff.get)

                        final_price = (end_date - start_date).days * room.price_per_day

                        is_this_start_date_earlier_than_nearest_start_date = (start_date - nearest_start_date).days < 0

                        if is_this_start_date_earlier_than_nearest_start_date:
                            RoomHistory.objects.create(start_date=start_date, end_date=end_date, room=room, user=user,
                                                       final_price=final_price)

                            room.is_reserved = True
                            room.reserved_by = user
                            room.days_to_stay = (end_date - start_date).days
                            final_price = (end_date - start_date).days * room.price_per_day
                            room.final_price = final_price
                            room.start_date = start_date
                            room.end_date = end_date

                            room.save()

                            days_to_stay = (end_date - start_date).days
                            UserReservationHistory.objects.create(user=user, room=room, start_date=start_date,
                                                                  end_date=end_date, days=days_to_stay)

                        else:
                            RoomHistory.objects.create(start_date=start_date, end_date=end_date, room=room, user=user,
                                                       final_price=final_price)

                            days_to_stay = (end_date - start_date).days
                            UserReservationHistory.objects.create(user=user, room=room, start_date=start_date,
                                                                  end_date=end_date, days=days_to_stay)

                        return Response({'message': 'Room has been reserved successfully.'},
                                        status=status.HTTP_201_CREATED)


class CheckReservationDates(APIView):
    def get(self, request):
        rooms = Room.objects.filter(is_reserved=True)

        for room in rooms:
            date_to_be_passed_for_room_history_deletion = room.end_date
            if room.end_date <= timezone.now().date():
                room.is_reserved = False
                room.reserved_by = None
                room.start_date = None
                room.end_date = None
                room.final_price = None
                room.days_to_stay = None
                room.save()

                today = timezone.now().date()
                room_history_dates = RoomHistory.objects.filter(room=room, start_date__gt=today).values_list(
                    "start_date", flat=True).order_by("start_date")

                room_history_to_delete = RoomHistory.objects.get(
                    end_date=date_to_be_passed_for_room_history_deletion)

                try:
                    if room_history_dates is not None:
                        best_fit = room_history_dates.first()

                        room_history = RoomHistory.objects.get(start_date=best_fit)

                        room.start_date = room_history.start_date
                        room.end_date = room_history.end_date
                        room.reserved_by = room_history.user
                        room.is_reserved = True
                        room.days_to_stay = (room_history.end_date - room_history.start_date).days
                        room.final_price = room.price_per_day * (room_history.end_date - room_history.start_date).days

                        room.save()

                        room_history_to_delete.delete()

                    else:
                        room.start_date = None
                        room.end_date = None
                        room.reserved_by = None
                        room.is_reserved = False
                        room.days_to_stay = None
                        room.final_price = None

                        room.save()

                        room_history_to_delete.delete()

                except RoomHistory.DoesNotExist:
                    room_history_to_delete.delete()

        return Response({"message": "All rooms reservation dates have been checked."})
