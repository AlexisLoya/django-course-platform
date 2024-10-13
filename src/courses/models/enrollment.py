from django.db import models
from django.conf import settings
from .course import Course
from .lesson import Lesson, Progress
from exams.models import ExamAttempt

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

    def calculate_course_progress(self):
        total_lessons = Lesson.objects.filter(course=self.course).count()
        completed_lessons = Progress.objects.filter(user=self.user, lesson__course=self.course, completed=True).count()
        if total_lessons > 0:
            lesson_progress = (completed_lessons / total_lessons) * 70
            exam_progress = 30 if ExamAttempt.is_exam_completed(self.user, self.course) else 0
            return lesson_progress + exam_progress
        return 0