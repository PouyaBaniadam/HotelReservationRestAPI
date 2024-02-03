from random import randint
from uuid import uuid4

import requests.exceptions
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import account.models
from account.models import CustomUser, OTP
from account.sms import send_forget_password_code_sms
from reservation.models import UserReservationHistory
from reservation.serializers import UserReservationHistorySerializer


class LogInView(APIView):
    def post(self, request):
        username_or_phone = request.data.get('username_or_phone')
        password = request.data.get('password')

        if str(username_or_phone).isdigit():
            try:
                user = CustomUser.objects.get(phone=username_or_phone)
                authenticated_user = authenticate(self.request, username=user, password=password)
            except account.models.CustomUser.DoesNotExist:
                user = None
                authenticated_user = None
        else:
            try:
                user = CustomUser.objects.get(username=username_or_phone)
                authenticated_user = authenticate(self.request, username=user, password=password)
            except account.models.CustomUser.DoesNotExist:
                user = None
                authenticated_user = None

        if authenticated_user is not None:
            response = "success"
            authentication_token = user.authentication_token

        else:
            response = "failed"
            authentication_token = "failed"

        return Response({'message': response, "authentication_token": authentication_token}, status=status.HTTP_200_OK)


class RegisterView(APIView):
    def post(self, request):
        try:
            username = request.data.get('username')
            phone = request.data.get('phone')
            password = request.data.get('password')

            try:
                user_exists = CustomUser.objects.get(username=username)
            except:
                user_exists = None
            try:
                phone_exists = CustomUser.objects.get(phone=phone)
            except:
                phone_exists = None

            if user_exists is None and phone_exists is None:
                code = randint(1000, 9999)
                token = str(uuid4())

                print(code)

                # send_register_sms(receptor=phone, code=code)

                OTP.objects.create(phone=phone, code=code, token=token, username=username, password=password,
                                   type="phone_register_mode")
                return Response({'status': 'success', 'token': token}, status=status.HTTP_200_OK)

            elif user_exists is None and phone_exists is not None:
                return Response({'status': 'failed', 'message': 'There is already a user with this phone number.'},
                                status=status.HTTP_406_NOT_ACCEPTABLE)

            elif user_exists is not None and phone_exists is None:
                return Response({'status': 'failed', 'message': 'There is already a user with this username.'},
                                status=status.HTTP_406_NOT_ACCEPTABLE)

            elif user_exists is not None and phone_exists is not None:
                return Response(
                    {'status': 'failed', 'message': 'There is already a user with this phone number and username.'},
                    status=status.HTTP_406_NOT_ACCEPTABLE)

        except requests.exceptions.ConnectionError:
            return Response({'status': 'failed', 'message': "Can't send any sms code!"})

        except Exception as e:
            return Response({"status": "failed",
                             "message": f"{e}"})


class CheckOTPView(APIView):
    def post(self, request):
        token = request.data.get('token')
        code = request.data.get('code')
        check_type = request.data.get('type')

        if check_type == "phone_register_mode":
            try:
                otp = OTP.objects.get(token=token, code=code)

                authentication_token = str(uuid4())

                CustomUser.objects.create_user(phone=otp.phone, username=otp.username, password=otp.password,
                                               authentication_token=authentication_token)

                return Response({"status": "success",
                                 "message": f"Your account has been successfully created and now you are logged in as {otp.username}.\n\nYou also have been rewarded 10 free tokens!",
                                 "authentication_token": authentication_token})

            except:
                return Response({"status": "failed", "message": "Invalid code!"})

        if check_type == "forget_password_mode":

            try:
                otp = OTP.objects.get(token=token, code=code, type="forget_password_mode")
                user = CustomUser.objects.get(phone=otp.phone)
                authentication_token = user.authentication_token
            except:
                user = None

            if user is not None:
                return Response({"status": "success",
                                 "message": f"Your password has been changed successfully and noy you are logged in as {user.username}",
                                 "token": token, "authentication_token": authentication_token},
                                status=status.HTTP_200_OK)
            else:
                return Response({"status": "failed", "message": "Invalid code!"}, status=status.HTTP_401_UNAUTHORIZED)


class ForgetPasswordView(APIView):
    def post(self, request):
        username_or_phone = request.data.get('username_or_phone')

        try:
            if str(username_or_phone).isdigit():
                user = CustomUser.objects.get(phone=username_or_phone)
            else:
                user = CustomUser.objects.get(username=username_or_phone)

            receptor = user.phone

            code = randint(1000, 9999)
            token = str(uuid4())

            send_forget_password_code_sms(receptor=receptor, code=code)

            OTP.objects.create(phone=receptor, code=code, token=token, type="forget_password_mode")

            return Response({'token': token, 'status': 'success'})

        except requests.exceptions.ConnectionError:
            return Response({'status': 'failed', 'message': "Can't send any sms code!"})

        except Exception as e:
            return Response({"status": "failed",
                             "message": f"{e}"})


class ChangePassword(APIView):
    def post(self, request):
        new_password = request.data.get('password')
        token = request.data.get('token')

        retrieved_user = OTP.objects.get(token=token)

        username = CustomUser.objects.get(phone=retrieved_user)
        user = CustomUser.objects.get(username=username)
        authentication_token = user.authentication_token

        user.set_password(new_password)
        user.save()

        return Response({"status": "success", "message": "Your password has been changed.",
                         "authentication_token": authentication_token})


class History(APIView):
    def get(self, request, *args, **kwargs):
        try:
            authentication_token = request.data.get('authentication_token')

            user = CustomUser.objects.get(authentication_token=authentication_token)
            history = UserReservationHistory.objects.filter(user=user)

            history = UserReservationHistorySerializer(history, many=True).data

            return Response({"history": history}, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({'error': 'The user is invalid.'}, status=status.HTTP_404_NOT_FOUND)
