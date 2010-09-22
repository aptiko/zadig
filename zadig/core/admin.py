from django.contrib import admin
import models

admin.site.register(models.Language)

class StatePermissionInline(admin.TabularInline):
    model = models.StatePermission
class StateAdmin(admin.ModelAdmin):
    inlines = (StatePermissionInline,)
admin.site.register(models.State, StateAdmin)

admin.site.register(models.StateTransition)
admin.site.register(models.Workflow)
