#from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import Users, Papers

@admin.register(Users)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        (None, {'fields': ('interests',)}),
    )
    list_display = ('email', 'username', 'is_staff', 'is_active')

@admin.register(Papers)
class PapersAdmin(admin.ModelAdmin):
    list_display = ('title', 'authors', 'created_at')
    search_fields = ('title', 'authors')
