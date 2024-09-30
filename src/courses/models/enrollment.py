from django.db import models
from django.contrib.auth import get_user_model
from .course import Course

User = get_user_model()


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='enrollments', on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'course')
        
    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"
