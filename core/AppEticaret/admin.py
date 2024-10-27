from django.contrib import admin
from .models import *
from modeltranslation.admin import TranslationAdmin


@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    pass


admin.site.register(BasketProduct)
admin.site.register(Profil)
admin.site.register(Adress)
admin.site.register(Favorite)
admin.site.register(Comment)


@admin.register(Brand)
class ProductAdmin(TranslationAdmin):
    pass


@admin.register(Gender)
class GenderAdmin(TranslationAdmin):
    pass


@admin.register(Color)
class ColorAdmin(TranslationAdmin):
    pass


@admin.register(CaseShape)
class CaseShapeAdmin(TranslationAdmin):
    pass


@admin.register(StrapType)
class StrapTypeAdmin(TranslationAdmin):
    pass


@admin.register(GlassFeature)
class GlassFeatureAdmin(TranslationAdmin):
    pass


@admin.register(Style)
class StyleAdmin(TranslationAdmin):
    pass


@admin.register(Mechanism)
class MechanismAdmin(TranslationAdmin):
    pass
