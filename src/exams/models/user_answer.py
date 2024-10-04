from django.db import models
from .exam_attempt import ExamAttempt
from .question import Question
from .choice import Choice

class UserAnswer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    
    def check_if_correct(self):
        self.is_correct = self.selected_choice.is_correct
        self.save()