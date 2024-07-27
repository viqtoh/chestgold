from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *
from django.utils.translation import gettext_lazy as _

# Register your models here.



admin.site.register(Transaction)
class UserAdmin(BaseUserAdmin):
    ordering = ("id", "email")
    search_fields = ("email",)
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "transactions",
                    "first_name",
                    "last_name",
                    "date_of_birth",
                    "gender",
                    "profile_pic",
                    "phone",
                    "address",
                    "city",
                    "state",
                    "postal_code",
                    "email_confirmation_code","otpt"
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )


admin.site.register(User, UserAdmin)


admin.site.register(Address)