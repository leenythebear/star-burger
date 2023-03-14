from django.contrib import admin

from addresses.models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'address',
        'lat',
        'lon',
        'updated_at',
    ]
