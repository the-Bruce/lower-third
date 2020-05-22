from django.contrib import admin
from .models import Program, Scene, ProgramScene, Session


# Register your models here.
class SceneList(admin.StackedInline):
    model = ProgramScene


class ProgramAdmin(admin.ModelAdmin):
    inlines = [SceneList]


admin.site.register(Program, ProgramAdmin)
admin.site.register(Scene)
admin.site.register(Session)