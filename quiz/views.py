import json
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.core.files import File
# import os
from django import forms
from .utility import extract_text_from_pdf, extract_questions_from_text
from pdfminer.high_level import extract_text
from .models import Quiz, QuizAttempt, QuizReport, QuizSubmission, UploadedFile, Question

from django.contrib.auth.decorators import login_required
# import openai
# # Create your views here.
# import textwrap

# # Google generative ai
import google.generativeai as genai

# from IPython.display import display
# from IPython.display import Markdown


# def to_markdown(text):
#   text = text.replace('•', '  *')
#   return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))
# ends here


class UploadFileForm(forms.Form):
    file = forms.FileField()
    question_info = forms.ModelChoiceField(queryset=Quiz.objects.all(), empty_label=None, label='Subject')


@login_required
def upload_quiz(request):
    form = UploadFileForm()  # Initialize the form outside the if block
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            question_info = form.cleaned_data['question_info']
            uploaded_file = UploadedFile(file=request.FILES['file'])
            uploaded_file.save()
            file_path = uploaded_file.file.path
            pdf_text = extract_text_from_pdf(file_path)
            extracted_questions = extract_questions_from_text(pdf_text)

            genai.configure(api_key="AIzaSyBbMV9uVJ9mGCJ0UYlxp0Y7W_Jms62MyI4")
            generation_config = {
            "temperature": 0,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 400,
            }
            safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
            ]


            model = genai.GenerativeModel('gemini-pro')
            for key, question_data in extracted_questions.items():
                question_info = question_info
                question = question_data['question']
                optionA = question_data['options'].get('A', '')  # Default value '' if 'A' key is not found
                optionB = question_data['options'].get('B', '')  # Default value '' if 'B' key is not found
                optionC = question_data['options'].get('C', '')  # Default value '' if 'C' key is not found
                optionD = question_data['options'].get('D', '')  # Default value '' if 'D' key is not found
                optionE = question_data['options'].get('E', '')  # Default value '' if 'E' key is not found
                
                # use Ai here
                options = [f"{key}: {option}" for key, option in question_data['options'].items()]
                prompt = f"Question: {question}\nOptions: {' | '.join(options)}\n Answer:"
               
                # print(prompt)
                response = model.generate_content(prompt, safety_settings=safety_settings)
                specific_answer = response.candidates[0].content.parts[0].text
                print(specific_answer)
                correct_options = specific_answer

                new_question = Question(
                    question_number=key,
                    question_text=question,
                    optionA=optionA,
                    optionB=optionB,
                    optionC=optionC,
                    optionD=optionD,
                    optionE=optionE,
                    option_answer=correct_options,
                    question_info=question_info,
                )
                # Save the new question to the database
                new_question.save()
            quiz_id = question_info.id 
            return redirect('quiz:quiz_list', quiz_id=quiz_id)

            

        else:
            form = UploadFileForm()
            return render(request, "quiz/index.html", {'form': form})

    return render(request, "quiz/index.html", {'form': form}) 

@login_required
def quiz_list(request, quiz_id):
    quiz_id = int(quiz_id)
    uploaded_questions = Question.objects.filter(question_info__id=quiz_id)
    return render(request, 'quiz/quiz_preview.html', {'questions': uploaded_questions})

from django_ckeditor_5.widgets import CKEditor5Widget
class QuestionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)
          self.fields["question_text"].required = False
    class Meta:
        model = Question
        fields = ['question_number', 'question_text', 'optionA', 'optionB', 'optionC', 'optionD', 'optionE', 'theory_Answer', 'option_answer']
        widgets = {
              "question_text": CKEditor5Widget(
                  attrs={"class": "django_ckeditor_5"}, config_name="extends"
              )
          }
        
@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('quiz:quiz_list', question_title=question.title)  # Redirect to the quiz questions page after saving
    else:
        form = QuestionForm(instance=question)
    return render(request, 'quiz/edit_question.html', {'form': form})

@login_required
def quiz(request, pk):
    if not request.user.student.is_student:
        return HttpResponse("You are not authorized to access this page.")
    
    if QuizAttempt.objects.filter(student=request.user.student, quiz=pk).exists():
        return HttpResponse("You have already attempted this quiz.")
    
    student = request.user.student
    quiz_data = get_object_or_404(Quiz, pk=pk)
    uploaded_questions = Question.objects.filter(question_info__id=pk)
    return render(request, "quiz/quiz.html", {'questions': uploaded_questions,'quiz_data': quiz_data, 'student': student })


@login_required
def quiz_dashboard(request):
    if not request.user.student.is_student:
        return HttpResponse("You are not authorized to access this page because you are either not a student or not logged in!")

    student = request.user.student
    student_class = student.student_class

    # Retrieve active quizzes available for the student's class
    active_quizzes = Quiz.objects.filter(available_classes=student_class, is_active=True)

    # Exclude quizzes that the student has already attempted
    attempted_quizzes = QuizAttempt.objects.filter(student=student)
    for attempt in attempted_quizzes:
        active_quizzes = active_quizzes.exclude(pk=attempt.quiz.pk)

    context = {
        'student': student,
        'active_quizzes': active_quizzes,
    }

    return render(request, 'quiz/student_quiz_dashboard.html', context)


def submit_quiz(request):
    if request.method == 'POST':
        # Get the JSON data from the request
        json_answers = request.POST.get('json_answers')

        # Parse the JSON data
        answers = json.loads(json_answers)
        print(answers)
        # Get the user and quiz (you may need to adjust this based on your authentication and quiz logic)
        user = request.user
        quiz_id = request.POST.get('quiz_id')
        quiz = Quiz.objects.get(pk=quiz_id)

        # Save the submission to the database
        submission = QuizSubmission(user=user, quiz=quiz, answers=answers)
        submission.save()
        quiz_complete = QuizAttempt(student=user.student, quiz=quiz, is_completed=True)
        quiz_complete.save()

        # Redirect to a thank you page or another view
        return redirect('quiz:mark_questions', quiz_id=quiz_id)

def mark_questions(request, quiz_id):
    user = request.user
    quiz = QuizSubmission.objects.filter(is_marked = False)
    score = 0
    correct_options = []
    wrong_options = []
    for all_quiz in quiz:
        # print(all_quiz.answers)
        quiz_to_mark = all_quiz.quiz.pk

        questions_in_quiz = Question.objects.filter(question_info__id=quiz_to_mark)
        genai.configure(api_key="AIzaSyBbMV9uVJ9mGCJ0UYlxp0Y7W_Jms62MyI4")
        generation_config = {
            "temperature": 0,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 400,
            }
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
            ]


        model = genai.GenerativeModel('gemini-pro')

        for k, d in all_quiz.answers.items():
            # print(k,d)
            for x in questions_in_quiz:
                if x.question_number == k:
                    prompt = f'Correct Option:({x.option_answer}) | USERS answer is ({d}) if correct say "True"'
                    response = model.generate_content(prompt, safety_settings=safety_settings)
                    specific_answer = response.candidates[0].content.parts[0].text

                    if specific_answer == "True":
                        score += 1
                        # correct_options = x 
    print(score)
    mquiz = Quiz.objects.get(pk=quiz_id)
    report = QuizReport(student = user.student, quiz=mquiz, score=score)
    report.save()
    return HttpResponse("Automatic marking")
    # Handle other HTTP methods or redirect if necessary



