from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from account.models import CustomUser, OTP


class CustomUserAdmin(UserAdmin):
    list_display = ('phone', 'username', 'is_staff', 'is_superuser')

    search_fields = ('phone', 'username', 'first_name', 'last_name')
    readonly_fields = ('date_joined',)
    list_filter = ('is_staff',)
    list_per_page = 50
    ordering = ('-date_joined',)
    search_help_text = 'جستجو بر اساس شماره تلفن، نام کاربری، نام، نام خانوادگی و آدرس ایمیل'

    list_editable = ()
    filter_horizontal = ()
    fieldsets = ()


admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(OTP)
