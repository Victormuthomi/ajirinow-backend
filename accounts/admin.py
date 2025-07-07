from django.contrib import admin
from .models import User, FundiProfile, ClientProfile

admin.site.register(User)
admin.site.register(FundiProfile)
admin.site.register(ClientProfile)

