from django.db import models
from django.conf import settings
from django.urls import reverse
from .course import Course

class Exam(models.Model):
    public_id = models.CharField(max_length=130, blank=True, null=True, db_index=True)
    course = models.OneToOneField(Course, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    passing_percentage = models.PositiveIntegerField(default=90)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tries_allowed_per_day = models.PositiveIntegerField(default=1)
    time_limit = models.PositiveIntegerField(default=60)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Exam for {self.course.title}"
    
    
class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    
    def __str__(self):
        return self.text
    

class Choice(models.Model):
    CHOICE_LABELS = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    label = models.CharField(max_length=1, choices=CHOICE_LABELS)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.label}. {self.text}"
    
    
class ExamAttempt(models.Model):
    public_id = models.CharField(max_length=130, blank=True, null=True, db_index=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    passed = models.BooleanField(default=False)
    date_started = models.DateTimeField(auto_now_add=True)
    date_ended = models.DateTimeField(null=True, blank=True)
    
    
    def __str__(self):
        return f"{self.user.email}'s attempt at {self.exam.course.title}"
    
    def check_if_passed(self):
        if self.score is not None:
            self.passed = self.score >= self.exam.passing_percentage
            self.save()
    

class UserAnswer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    
    def check_if_correct(self):
        self.is_correct = self.selected_choice.is_correct
        self.save()