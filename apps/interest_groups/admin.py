from django.contrib import admin
from interest_groups.models import InterestGroup

class InterestGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'creator', 'created')

admin.site.register(InterestGroup, InterestGroupAdmin)
