from django import forms
from .models import Lesson
from django_summernote.widgets import SummernoteWidget

class LessonInlineForm(forms.ModelForm):
    content = forms.CharField(widget=SummernoteWidget(), required=False)
    
    class Meta:
        model = Lesson
        fields = '__all__'
        