from django.contrib import admin
from ftft.canzoni.models import canzone, licenze, deposito

# Register your models here.

admin.site.register(licenze)
admin.site.register(canzone)
admin.site.register(deposito)
