from django.contrib import admin
from .models import DayCount, LogItem
from rangefilter.filter import DateRangeFilter


class LogAdmin(admin.ModelAdmin):
    readonly_fields = ('time', 'deviceID', 'userID', 'delta')
    list_filter = (('time',DateRangeFilter),)
    list_display = ('time', 'delta', 'deviceID', 'userID')
    ordering = ('time',)


class DayCountAdmin(admin.ModelAdmin):
    list_display = ('date', 'peak', 'total')
    list_display_links = ('date',)
    readonly_fields = ('peak', 'date', 'total')


# Register your models here.
admin.site.register(DayCount, DayCountAdmin)
admin.site.register(LogItem, LogAdmin)
