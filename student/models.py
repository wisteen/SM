import random
import string

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

def generate_cbt_code():
    """Generate a unique 4-digit CBT code."""
    while True:
        cbt_code = ''.join(random.choices(string.digits, k=9))
        if not Student.objects.filter(cbt_code=cbt_code).exists():
            return cbt_code
        
# Create your models here.
class Student(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    date_of_birth = models.DateField( blank=True, null=True)
    phone_number = models.CharField(max_length=20,  null= True, blank=True)
    parents_details = models.CharField(max_length=20,  null= True, blank=True)
    address = models.CharField(max_length=20,  null= True, blank=True)
    profile_picture = models.ImageField(upload_to='student_profile_pics/', blank=True, null=True)
    category = models.CharField(max_length=20, choices=[('teacher', 'teacher'), ('student', 'student')], default='student')
    student_class = models.ForeignKey('ClassName', on_delete=models.CASCADE, blank=True, null=True)
    cbt_code = models.CharField(max_length=9, unique=True, default=generate_cbt_code)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.user.username
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Student.objects.create(user=instance)


class ClassName(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name