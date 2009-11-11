from django.contrib import admin
import models

admin.site.register(models.Language)
admin.site.register(models.Site)
admin.site.register(models.ContentFormat)

class PageInline(admin.StackedInline): model = models.Page
class MetatagsInline(admin.TabularInline): model = models.VObjectMetatags
class PageEntryAdmin(admin.ModelAdmin):
    inlines = [PageInline, MetatagsInline]
admin.site.register(models.Entry, PageEntryAdmin)
