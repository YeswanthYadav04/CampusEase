# chatbot/translation.py
from modeltranslation.translator import translator, TranslationOptions
from .models import Document, FAQ

class DocumentTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

class FAQTranslationOptions(TranslationOptions):
    fields = ('question', 'answer')

translator.register(Document, DocumentTranslationOptions)
translator.register(FAQ, FAQTranslationOptions)