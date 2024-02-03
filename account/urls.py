from django.urls import path
from . import views
from .views import History

app_name = "account"

urlpatterns = [
    path("login", views.LogInView.as_view(), name="login"),
    path("register", views.RegisterView.as_view(), name="register"),
    path("otp/check", views.CheckOTPView.as_view(), name="check_otp"),
    path('history', History.as_view(), name='history'),
]
