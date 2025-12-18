from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
import json

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Студент'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student'
    )
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    telegram_connected = models.BooleanField(default=False)
    telegram_id = models.CharField(max_length=100, blank=True)
    education_goal = models.CharField(max_length=50, blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    
    # Уведомления
    notifications = models.JSONField(default={
        'deadline_reminders': True,
        'scholarship_updates': True,
        'system_notifications': True
    })
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class University(models.Model):
    TYPE_CHOICES = [
        ('Top', 'Топовый университет'),
        ('Accessible', 'Доступный университет'),
    ]
    
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    flag = models.CharField(max_length=10)  # Emoji
    disciplines = models.JSONField(default=list)
    ranking = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='university_logos/', null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.country})"

class Program(models.Model):
    TYPE_CHOICES = [
        ('Full', 'Полная стипендия'),
        ('Partial', 'Частичная стипендия'),
        ('Self-funded', 'Самофинансирование'),
        ('Government', 'Государственный грант'),
    ]
    
    LEVEL_CHOICES = [
        ('Bachelor', 'Бакалавриат'),
        ('Master', 'Магистратура'),
        ('PhD', 'Докторантура'),
    ]
    
    university = models.ForeignKey(
        University, 
        on_delete=models.CASCADE,
        related_name='programs'
    )
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    flag = models.CharField(max_length=10)  # Emoji
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    discipline = models.CharField(max_length=100)
    deadline = models.DateField()
    description = models.TextField()
    url = models.URLField(blank=True)
    logo = models.ImageField(upload_to='program_logos/', null=True, blank=True)
    
    # Что покрывает
    coverage = models.JSONField(default={
        'tuition': False,
        'accommodation': False,
        'insurance': False,
        'flight': False
    })
    
    # Требования
    requirements = models.JSONField(default={
        'gpa': '',
        'language': '',
        'citizenship': '',
        'additional': []
    })
    
    # Документы
    documents = models.JSONField(default=list)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.university.name}"

class Favorite(models.Model):
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

class Application(models.Model):
    STATUS_CHOICES = [
        ('watching', 'Смотрю'),
        ('preparing', 'Подготавливаю документы'),
        ('applied', 'Подал заявку'),
        ('accepted', 'Принят'),
        ('rejected', 'Отклонен'),
    ]
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='watching'
    )
    notes = models.TextField(blank=True)
    documents_submitted = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'program']

class AIHistory(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='ai_history'
    )
    query = models.TextField()
    response = models.TextField()
    tokens_used = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

class ContactRequest(models.Model):
    MODE_CHOICES = [
        ('telegram', 'Telegram Bot'),
        ('email', 'Email'),
        ('phone', 'Phone Call'),
    ]
    
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    countries = models.JSONField(default=list)
    preferred_mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='new')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)