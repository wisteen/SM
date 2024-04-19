from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.auth.models import User

from student.models import ClassName, Student

# Create your models here.
class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    
class Assessment(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Quiz(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE,blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    question_type = models.CharField(max_length=50, choices=[('Theory', 'Theory'), ('Objectives', 'Objectives')])
    duration = models.CharField(max_length=4, blank=True, null=True, choices=[('1', '1 Mins'),('20', '20 Mins'),('30', '30 Mins'), ('40','40 Mins'),('50','50 Mins'),('60','60 Mins'),('90','90 Mins'),('120','120 Mins'),])
    date_of_exam = models.DateTimeField(verbose_name="Date Of Exam", auto_now=True)
    total_score = models.CharField(max_length=50, choices=[('20', '20%'), ('30', '30%'), ('40','40%'), ('50','50%'),('60','60%')])
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE,blank=True, null=True)
    available_classes = models.ManyToManyField(ClassName)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    question_info = models.ForeignKey(Quiz, on_delete=models.CASCADE,blank=True, null=True)
    question_number = models.CharField(max_length=50, blank=True, null=True)
    question_text = CKEditor5Field('Question', config_name='extends')
    optionA = models.CharField(max_length=50, blank=True, null=True)
    optionB = models.CharField(max_length=50, blank=True, null=True)
    optionC = models.CharField(max_length=50, blank=True, null=True)
    optionD = models.CharField(max_length=50, blank=True, null=True)
    optionE = models.CharField(max_length=50, blank=True, null=True)
    theory_Answer = CKEditor5Field('Theory Answer', config_name='extends', blank=True, null=True)
    option_answer = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return self.question_text


class UploadedFile(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class QuizSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Assuming you have a User model
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)  # Assuming you have a Quiz model
    answers = models.JSONField()
    is_marked= models.BooleanField(default=False)


class QuizAttempt(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    class Meta:
        unique_together = ('student', 'quiz')

    def __str__(self):
        return f'{self.student.user.username} - {self.quiz.title}'


class QuizReport():
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score = models.CharField(max_length=50, blank=True, null=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)