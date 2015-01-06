from django.contrib import admin
from retrato.auth.models import FacebookUser
from django.utils import timezone


def authorize(modeladmin, request, queryset):
    queryset.update(date_authorized=timezone.now())
authorize.short_description = "Authorize user"


def revoke_authorization(modeladmin, request, queryset):
    queryset.update(date_authorized=None)
revoke_authorization.short_description = "Revoke user authorization"


class FacebookUserAdmin(admin.ModelAdmin):
    readonly_fields = ('userID', 'first_name', 'last_name')
    fields = ('userID', 'first_name', 'last_name', 'date_authorized')
    list_display = ('userID', 'full_name', 'date_authorized')
    actions = [authorize, revoke_authorization]

    def full_name(self, obj):
        return ("%s %s" % (obj.first_name, obj.last_name))
    full_name.short_description = 'Name'


admin.site.register(FacebookUser, FacebookUserAdmin)
