from django.contrib import admin
from adminsortable2.admin import SortableInlineAdminMixin
from .models import Program, Scene, ProgramScene, Session


# Register your models here.
class SceneList(SortableInlineAdminMixin, admin.StackedInline):
    model = ProgramScene
    extra = 0


class SceneListExtra(SortableInlineAdminMixin, admin.StackedInline):
    model = ProgramScene
    extra = 5


class ProgramAdmin(admin.ModelAdmin):
    inlines = [SceneList]
    save_on_top = True
    save_as = True

    def add_view(self, request, form_url='', extra_context=None):
        self.inlines = [SceneListExtra]
        return super().add_view(request, form_url, extra_context)


admin.site.register(Program, ProgramAdmin)
admin.site.register(Scene)
admin.site.register(Session)
