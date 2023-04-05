import secrets
import time
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import get_object_or_404
from Login.models import UserType
from django.shortcuts import render, redirect, get_object_or_404
from .models import Quiz, Question, Answer


# @csrf_protect
def dashboard_view(request):
    quizzes = Quiz.objects.filter(user_id=request.user.id)
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
    return render(request, 'dashboard.html', {'quizzes': quizzes})


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
    return redirect('login_view')


def unauthorized(request):
    return render(request, 'unauthorized.html')


def create_quiz(request):
    if request.method == 'POST':
        # Get the name, subject, and grade level from the request
        name = request.POST['name']
        subject = request.POST['subject']
        grade_level = request.POST['grade_level']
        num_ques = request.POST['num_ques']
        quiz_pw = request.POST['quiz_pw']

        # Query the database for the current user_id
        current_user = request.user  # Get the current user from the request
        user_id = current_user.id  # Get the user_id from the current user

        # Create a Quiz object and add it to the database
        quiz = Quiz(name=name, subject=subject,
                    grade_level=grade_level, num_ques=num_ques,
                    user_id=user_id, quiz_pw=quiz_pw)
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
        question = Question(quiz_id=quiz_id, text=text, duration=60, order=question_number)
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


def student_dashboard_view(request):
    # Redirect the user if they are not logged in
    if not request.user.is_authenticated:
        return redirect('login')

    # Get the user's type
    try:
        user_type = UserType.objects.get(id=request.user.id).user_type
    except UserType.DoesNotExist:
        return redirect('unauthorized')

    # Redirect the user if they do not have the required permissions
    if user_type != "student":
        return redirect('unauthorized')

    if request.method == 'POST':
        # Extract quiz-id and quiz-password from the request
        quiz_id = request.POST.get('quiz-id')
        quiz_pw = request.POST.get('quiz-password')

        # Check if the quiz_id and quiz_pw are valid
        try:
            quiz = Quiz.objects.get(id=quiz_id, quiz_pw=quiz_pw)
            return redirect('start_quiz', quiz_id=quiz.id)
        except Quiz.DoesNotExist:
            # If quiz_id and quiz_pw combination is not valid, render the student_dashboard.html again
            return render(request, 'student_dashboard.html', {'error_message': 'Invalid quiz number or password'})

    # Handle GET request
    else:
        return render(request, 'student_dashboard.html')


def take_quiz(request, quiz_id, question_num):
    # Redirect the user if they are not logged in
    if not request.user.is_authenticated:
        return redirect('login')

    # Get the user's type
    try:
        user_type = UserType.objects.get(id=request.user.id).user_type
    except UserType.DoesNotExist:
        return redirect('unauthorized')

    # Redirect the user if they do not have the required permissions
    if user_type != "student":
        return redirect('unauthorized')

    # Check if the quiz exists in the database
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Get the questions and answers for the quiz
    questions = Question.objects.filter(quiz=quiz)
    num_ques = questions.count()

    if question_num > num_ques:
        return redirect('student_dashboard')

    current_question = questions[question_num - 1]
    current_answers = Answer.objects.filter(question=current_question)

    return render(request, 'take_quiz.html', {
        'quiz': quiz,
        'current_question_num': question_num,
        'num_ques': num_ques,
        'current_question': current_question,
        'current_answers': current_answers
    })

def start_quiz(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    quiz_name = quiz.name
    quiz_subject = quiz.subject
    quiz_grade_level = quiz.grade_level
    quiz_num_ques = quiz.num_ques  # Updated to match the field name in the Quiz model
    quiz_pw = quiz.quiz_pw

    context = {
        'quiz_name': quiz_name,
        'quiz_subject': quiz_subject,
        'quiz_grade_level': quiz_grade_level,
        'quiz_num_ques': quiz_num_ques,
        'quiz_id': quiz_id,
        'quiz_pw': quiz_pw,
    }

    # Redirect to the 'take_quiz' view with the initial question_num set to 1
    return redirect('take_quiz', quiz_id=quiz_id, question_num=1)



def submit_answer(request, quiz_id, question_id):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        user_type = UserType.objects.get(id=request.user.id).user_type
    except UserType.DoesNotExist:
        return redirect('unauthorized')

    if user_type != "student":
        return redirect('unauthorized')

    quiz = get_object_or_404(Quiz, id=quiz_id)
    question = get_object_or_404(Question, id=question_id)

    if request.method == 'POST':
        answer_id = request.POST.get('answer')
        submitted_answer = get_object_or_404(Answer, id=answer_id)
        question.submitted_answer = submitted_answer
        question.save()

        # Redirect the user to the next question or the results page.
        # Implement the logic to determine the next question or results.
        return redirect('next_question_or_results')

    return redirect('take_quiz', quiz_id=quiz_id, quiz_pw=quiz.quiz_pw)
