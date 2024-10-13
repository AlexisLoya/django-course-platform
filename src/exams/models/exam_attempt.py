
from django.db import models
from django.conf import settings
from .exam import Exam
import uuid

class ExamAttempt(models.Model):
    public_id = models.CharField(max_length=130, blank=True, null=True, db_index=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    passed = models.BooleanField(default=False)
    date_started = models.DateTimeField(auto_now_add=True)
    date_ended = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.public_id:
            self.public_id = str(uuid.uuid4())
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.email}'s attempt at {self.exam.course.title}"
    
    def check_if_passed(self):
        if self.score is not None:
            self.passed = self.score >= self.exam.passing_percentage
            self.save()

    @staticmethod
    def is_exam_completed(user, course):
        taken = ExamAttempt.objects.filter(user=user, exam__course=course).first()
        return True if taken and taken.passed else False