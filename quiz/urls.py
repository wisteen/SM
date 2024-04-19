from django.urls import path, include
from .views import *
from django.conf.urls.static import static
from django.conf import settings

app_name = 'quiz'
urlpatterns = [
    path('', upload_quiz, name="upload_quiz" ),
    path('quiz_list/<int:quiz_id>/', quiz_list, name="quiz_list" ),
    path('edit-question/<int:question_id>/', edit_question, name='edit_question'),
    path('student_quiz/<int:pk>/', quiz, name='quiz'),
    path('quiz_dashboard', quiz_dashboard, name='quiz_dashboard'),
    path('submit_quiz', submit_quiz, name='submit_quiz'),
    path('mark_questions/<int:quiz_id>/', mark_questions, name='mark_questions'),
    
    path("ckeditor5/", include('django_ckeditor_5.urls'), name="ck_editor_5_upload_file"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)