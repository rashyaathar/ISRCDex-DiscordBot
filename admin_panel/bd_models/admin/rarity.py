from typing import TYPE_CHECKING, Any

from django.contrib import admin

from bd_models.models import RarityTier

if TYPE_CHECKING:
    from django.db.models import Field, Model, QuerySet
    from django.http import HttpRequest

@admin.register(RarityTier)
class RarityAdmin(admin.ModelAdmin):
    list_display = ("rarity_tier", "threshold", "enabled_tier")
    list_editable = ("threshold", "enabled_tier")
    ordering = ("threshold",)
    fields = ("rarity_tier", "threshold", "enabled_tier")