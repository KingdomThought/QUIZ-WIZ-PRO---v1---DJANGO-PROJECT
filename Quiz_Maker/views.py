import secrets
import time
from django.shortcuts import render, redirect

from Login.models import UserType
from .models import Quiz, Question, Answer, Assignment, Course


# @csrf_protect
def dashboard_view(request):
    if request.user.is_authenticated:
        # Get the user's type
        user_type = UserType.objects.get(id=request.user.id).user_type
        # Redirect the user if they do not have the required permissions
        if user_type != "teacher_administrator":
            return redirect('unauthorized')
    else:
        # Redirect the user if they are not logged in
        return redirect('login')

    # Render the teacher dashboard template
    return render(request, 'dashboard.html')


def home_view(request):
    if request.user.is_authenticated:
        # Get the user's type
        user_type = UserType.objects.get(id=request.user.id).user_type
        if user_type == "teacher_administrator":
            # Redirect to the teacher/administrator dashboard
            return redirect('dashboard')
        elif user_type == "student":
            # Redirect to the student dashboard
            return redirect('student_dashboard')
    # Redirect to the login page if the user is not logged in
    return redirect('login')


def student_dashboard_view(request):
    if request.user.is_authenticated:
        # Get the user's type
        user_type = UserType.objects.get(id=request.user.id).user_type
        # Redirect the user if they do not have the required permissions
        if user_type != "student":
            return redirect('unauthorized')
    else:
        # Redirect the user if they are not logged in
        return redirect('login')

    # Render the student dashboard template
    return render(request, 'student_dashboard.html')


def unauthorized(request):
    return render(request, 'unauthorized.html')


def create_quiz(request):
    if request.method == 'POST':
        # Get the name, subject, and grade level from the request
        name = request.POST['name']
        subject = request.POST['subject']
        grade_level = request.POST['grade_level']
        num_ques = request.POST['num_ques']

        # Create a Quiz object and add it to the database
        quiz = Quiz(name=name, subject=subject, grade_level=grade_level, num_ques=num_ques)
        quiz.save()

        # Query the database for the id of the Quiz model
        quiz_id = quiz.id
        quiz_name = quiz.name

        # Call the create_question function, passing the num_ques argument
        return create_question(request, quiz_id=quiz.id, num_ques=(int(num_ques) + 1))
    else:
        # Render the create_question.html template
        return render(request, 'create_quiz.html')


def quiz_create_success(request):
    # Render the quiz_create_success.html template
    return render(request, 'quiz_create_success.html')


def create_question(request, quiz_id, num_ques):
    # Get the current number of questions for the quiz
    num_ques_created = Question.objects.filter(quiz_id=quiz_id).count()

    # Set the question_number variable to the current number of questions
    question_number = num_ques_created

    # Check if the request method is POST
    if request.method == 'POST':
        # Try to get the question text from the request.POST dictionary
        text = request.POST.get('question_text', '')  # Set the default value of text to an empty string

        # Get the answers from the request.POST dictionary
        answer_1 = request.POST.get('answer_1', "")
        answer_2 = request.POST.get('answer_2', "")
        answer_3 = request.POST.get('answer_3', "")
        answer_4 = request.POST.get('answer_4', "")

        # Create the question object
        question = Question(quiz_id=quiz_id, text=text, duration=60)
        question.save()

        # Create the answer objects
        if answer_1:
            a1 = Answer(text=answer_1, is_correct=True, question_id=question.id, order=question_number)
            a1.save()
        if answer_2:
            a2 = Answer(text=answer_2, is_correct=False, question_id=question.id, order=question_number)
            a2.save()
        if answer_3:
            a3 = Answer(text=answer_3, is_correct=False, question_id=question.id, order=question_number)
            a3.save()
        if answer_4:
            a4 = Answer(text=answer_4, is_correct=False, question_id=question.id, order=question_number)
            a4.save()

        # Decrement the number of questions
        num_ques = int(num_ques)
        num_ques -= 1

        # Increment the question_number variable by 1
        question_number += 1

        # If there are still questions left, reload the page
        if num_ques > 0:
            return redirect('create_question', quiz_id=quiz_id, num_ques=num_ques)
        else:
            return redirect('quiz_create_success')
    else:
        # If num_ques is 0 or less, redirect to the quiz_create_success page
        if num_ques <= 0:
            return redirect('quiz_create_success')

        # Render the create_question.html template
        return render(request, 'create_question.html',
                      {'quiz_id': quiz_id, 'num_ques': num_ques, 'question_number': question_number})


def quiz_edit(request):
    pass


def take_quiz(request, quiz_id):
    # Query the database for the quiz with the given quiz_id
    quiz = Quiz.objects.get(id=quiz_id)

    # Query the database for all of the questions in the quiz
    questions = Question.objects.filter(quiz_id=quiz_id)

    # Initialize the question_number variable to 1
    question_number = 1

    # Initialize the score variable to 0
    score = 0

    # If the request method is POST, process the submitted answers
    if request.method == 'POST':
        # Iterate through the questions
        for question in questions:
            # Get the submitted answer for the current question
            answer = request.POST.get(f'question_{question_number}', '')

            # If the submitted answer is correct, increment the score by 1
            if answer == question.correct_answer:
                score += 1

            # Increment the question_number variable by 1
            question_number += 1

        # Calculate the percentage score
        percentage_score = (score / len(questions)) * 100

        # Render the quiz_results.html template with the percentage_score and quiz_id variables
        return render(request, 'quiz_results.html', {'percentage_score': percentage_score, 'quiz_id': quiz_id})
