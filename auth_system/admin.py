from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account


class AccountAdmin(UserAdmin):
    list_display = ("email", "username", "is_active", "is_staff", "created_at")

    list_display_links = ("email", "username")

    search_fields = ("email", "username")

    list_filter = ("is_active", "is_staff", "is_superuser", "groups")

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        (
            "Permissions",
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
        ("Important dates", {"fields": ("last_login", "created_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    readonly_fields = ("created_at", "last_login")

    ordering = ("-created_at",)


admin.site.register(Account, AccountAdmin)
