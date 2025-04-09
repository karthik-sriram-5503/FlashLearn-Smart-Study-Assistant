from django import forms
from .models import PDFDocument, Summary, Flashcard

class PDFUploadForm(forms.ModelForm):
    class Meta:
        model = PDFDocument
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter document title'}),
            'file': forms.FileInput(attrs={'class': 'form-control'})
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.lower().endswith('.pdf'):
                raise forms.ValidationError("Only PDF files are allowed.")
            if file.size > 20 * 1024 * 1024:  # 20MB limit
                raise forms.ValidationError("File size cannot exceed 20MB.")
            return file
        else:
            raise forms.ValidationError("Please select a PDF file.")

class SummaryTopicForm(forms.Form):
    topic = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-select'}))
    
    def __init__(self, *args, topics=None, **kwargs):
        super().__init__(*args, **kwargs)
        if topics:
            self.fields['topic'].choices = topics

class FlashcardGenerationForm(forms.Form):
    num_cards = forms.IntegerField(
        min_value=1,
        max_value=20,
        initial=5,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

class ChatForm(forms.Form):
    message = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Type your question here...',
            'autocomplete': 'off'
        })
    )