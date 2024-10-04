from django.db import models
from django.conf import settings
from django.urls import reverse
from courses.models.course import Course
import uuid

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
    
    def save(self, *args, **kwargs):
        if not self.public_id:
            self.public_id = str(uuid.uuid4())
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Exam for {self.course.title}"
