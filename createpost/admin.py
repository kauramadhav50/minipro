from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Post

# This makes the new fields visible in the Admin dashboard
class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('fullname', 'bio', 'profile_pic')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Post)