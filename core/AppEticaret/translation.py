from .models import *
from modeltranslation.translator import TranslationOptions, register


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('model', 'description')


@register(Brand)
class BrandTranslationOptions(TranslationOptions):
    fields = ('brand',)


@register(Gender)
class GenderTranslationOptions(TranslationOptions):
    fields = ('gender',)


@register(Color)
class ColorTranslationOptions(TranslationOptions):
    fields = ('color',)


@register(CaseShape)
class CaseShapeTranslationOptions(TranslationOptions):
    fields = ('case_shape',)


@register(StrapType)
class StrapTypeShapeTranslationOptions(TranslationOptions):
    fields = ('strap_type',)


@register(GlassFeature)
class GlassFeatureTypeShapeTranslationOptions(TranslationOptions):
    fields = ('glass_feature',)


@register(Style)
class StyleFeatureTypeShapeTranslationOptions(TranslationOptions):
    fields = ('style',)


@register(Mechanism)
class MechanismFeatureTypeShapeTranslationOptions(TranslationOptions):
    fields = ('mechanism',)

