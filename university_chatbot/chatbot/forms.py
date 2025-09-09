# chatbot/forms.py
from django import forms
from .models import Document, FAQ

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'description', 'file', 'semester', 'subject', 'unit', 'doc_type']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'unit': forms.NumberInput(attrs={'min': 1, 'max': 10}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question', 'answer', 'category']
        widgets = {
            'question': forms.TextInput(attrs={'placeholder': 'Enter question'}),
            'answer': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter answer'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})