from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.account.models import User
from .forms import SignUpForm


# Register your models here.
@admin.register(User)
class UserAdmin(UserAdmin):
    add_form = SignUpForm
    model = User
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active",)
    list_filter = ("email", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profile", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
         ),
    )
    search_fields = ("email",)
    ordering = ("email",)
