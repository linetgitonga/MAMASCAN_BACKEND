# resources/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.conf import settings



class Resource(models.Model):
    TYPE_CHOICES = [
        ('VIDEO', 'Video'),
        ('DOCUMENT', 'Document'),
        ('INTERACTIVE', 'Interactive'),
        ('AUDIO', 'Audio'),
        ('QUIZ', 'Quiz'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
    ]
    
    CATEGORY_CHOICES = [
        ('DIAGNOSIS', 'Diagnosis'),
        ('SURGERY', 'Surgery'),
        ('TREATMENT', 'Treatment'),
        ('PREVENTION', 'Prevention'),
        ('RESEARCH', 'Research'),
        ('GENERAL', 'General'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    instructor = models.CharField(max_length=100)
    rating = models.DecimalField(
        max_digits=2, 
        decimal_places=1, 
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        default=0.0
    )
    downloadable = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # File fields for actual content
    video_file = models.FileField(upload_to='resources/videos/', blank=True, null=True)
    document_file = models.FileField(upload_to='resources/documents/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='resources/thumbnails/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Learning Resource'
        verbose_name_plural = 'Learning Resources'
    
    def __str__(self):
        return self.title
    
    @property
    def enrollments(self):
        return self.user_progress.count()
    
    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return sum(r.rating for r in ratings) / len(ratings)
        return 0.0


class UserProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learning_progress')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='user_progress')
    progress = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Progress percentage (0-100)"
    )
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    time_spent = models.PositiveIntegerField(default=0, help_text="Time spent in minutes")
    
    class Meta:
        unique_together = ['user', 'resource']
        ordering = ['-last_accessed']
        verbose_name = 'User Progress'
        verbose_name_plural = 'User Progress'
    
    def __str__(self):
        return f"{self.user.username} - {self.resource.title} ({self.progress}%)"
    
    def save(self, *args, **kwargs):
        # Auto-set completed if progress is 100%
        if self.progress >= 100 and not self.completed:
            self.completed = True
            self.completed_at = timezone.now()
        elif self.progress < 100 and self.completed:
            self.completed = False
            self.completed_at = None
        super().save(*args, **kwargs)


class ResourceRating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='ratings')
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'resource']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.resource.title} - {self.rating}"


class LearningPath(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    resources = models.ManyToManyField(Resource, through='LearningPathResource')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title


class LearningPathResource(models.Model):
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=1)
    is_required = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['learning_path', 'resource']
        ordering = ['order']