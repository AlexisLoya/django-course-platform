from django.db import models
from django.conf import settings
from .course import Course



class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='enrollments', on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    progress = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('user', 'course')
        
    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"
