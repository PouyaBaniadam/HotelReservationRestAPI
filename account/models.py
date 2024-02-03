import uuid

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.text import slugify


class CustomUserManager(BaseUserManager):
    def create_user(self, phone, username=None, email=None, password=None, **extra_fields):
        if not phone:
            raise ValueError('کاربر باید شماره تلفن داشته باشد.')

        if not username:
            raise ValueError('کاربر باید نام کاربری داشته باشد.')

        user = self.model(
            phone=self.normalize_phone(phone),
            username=username,
            email=self.normalize_email(email) if email else None,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('کارمند باید مقدار is_staff=True را داشته باشد.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('ابر کاربر باید مقدار is_staff=True را داشته باشد.')

        return self.create_user(phone, username, email, password, **extra_fields)

    def normalize_phone(self, phone):
        return ''.join(filter(str.isdigit, phone))


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(unique=True, max_length=30)
    phone = models.CharField(unique=True, max_length=11)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    national_id = models.CharField(max_length=10, blank=True, null=True)
    authentication_token = models.UUIDField(max_length=100, default=uuid.uuid4)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone']

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.username)
        self.username = self.username.lower()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class OTP(models.Model):
    phone = models.CharField(max_length=11)
    username = models.CharField(max_length=30, blank=True, null=True, default="")
    password = models.CharField(max_length=100, editable=False, blank=True, null=True, default="")
    code = models.CharField(max_length=5)
    token = models.CharField(max_length=36)
    type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    delete_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.phone}"
