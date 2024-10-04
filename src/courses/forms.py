from django import forms
from .models import Lesson, Exam, Question, Choice, UserAnswer
from django_summernote.widgets import SummernoteWidget

class LessonInlineForm(forms.ModelForm):
    content = forms.CharField(widget=SummernoteWidget(), required=False)
    
    class Meta:
        model = Lesson
        fields = '__all__'
        

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['passing_percentage']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']

ChoiceFormSet = forms.inlineformset_factory(
    Question,
    Choice,
    fields=('label', 'text', 'is_correct'),
    extra=4,
    max_num=4,
    widgets={'is_correct': forms.RadioSelect}
)

class UserAnswerForm(forms.ModelForm):
    class Meta:
        model = UserAnswer
        fields = ['selected_choice']
        widgets = {
            'selected_choice': forms.RadioSelect
        }
