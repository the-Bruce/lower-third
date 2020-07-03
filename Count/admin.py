from django.contrib import admin
from .models import DayCount

class DayCountAdmin(admin.ModelAdmin):
    list_display = ('date','peak','total')
    list_display_links = ('date',)
    readonly_fields = ('peak','date','total')

# Register your models here.
admin.site.register(DayCount, DayCountAdmin)