from django.contrib import admin
from .models import User, SunsetRatingEntry

class RatingInLine(admin.TabularInline):
    model = SunsetRatingEntry
    extra = 0

class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'first_login_date')
    inlines = [RatingInLine]

admin.site.register(User, UserAdmin)
admin.site.register(SunsetRatingEntry)