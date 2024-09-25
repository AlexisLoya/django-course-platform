from django.db import models


class AccessRequirement(models.TextChoices):
    ANYONE = "any", "Anyone"
    EMAIL_REQUIRED = "email", "Email required"


class PublishStatus(models.TextChoices):
    PUBLISHED = "publish", "Published"
    COMING_SOON = "soon", "Coming Soon"
    DRAFT = "draft", "Draft"
    
    
class LessonType(models.TextChoices):
    VIDEO = 'VIDEO', 'Video'
    BLOG = 'BLOG', 'Blog/Text'