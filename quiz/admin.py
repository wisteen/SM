from django.contrib import admin
from .models import *

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text','optionA', 'optionB', 'optionC', 'optionD', 'optionE', 'option_answer')
    search_fields = ['question_text']

# Register your models here.
admin.site.register(UploadedFile)
admin.site.register(Assessment)
admin.site.register(Subject)
admin.site.register(Quiz)
admin.site.register(QuizAttempt)
admin.site.register(QuizSubmission)
admin.site.register(Question, QuestionAdmin)
