import secrets

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.contrib.auth.models import User

from Login.models import UserType


# from Login.models import CustomUser


@csrf_protect
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}")
                # Check the user's type and redirect to the appropriate dashboard
                user_type = UserType.objects.get(id=user.id).user_type
                if user_type == "student":
                    return redirect('student_dashboard')
                elif user_type == "teacher_administrator":
                    return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
                return redirect('login_view')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login_view')
    form = AuthenticationForm()
    return render(request=request,
                  template_name="loginpage.html",
                  context={"form": form})


def logout_view(request):
    # Log the user out
    logout(request)

    # Redirect the user to the login page
    return redirect('login_view')


def forgot_password_view(request):
    if request.method == 'POST':
        # Handle the POST request and process the form data

        # Check if the provided email address is associated with an account
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user is None:
            # No user with the provided email address exists
            return render(request, 'forgotpassword.html', {
                'error': 'The provided email address is not associated with an account.'
            })

        # Generate a password reset token and send it to the user's email address
        token = generate_password_reset_token(user)
        send_password_reset_email(user, token)

        # Redirect to a confirmation page
        return redirect('accounts:forgot_password_confirmation')
    else:
        # Handle the GET request and display the form
        return render(request, 'forgotpassword.html')


def send_password_reset_email(user, token):
    # Render the email template
    subject = 'Password Reset Request'
    html_message = render_to_string('accounts/email/password_reset.html', {
        'user': user,
        'token': token,
    })
    text_message = render_to_string('accounts/email/password_reset.txt', {
        'user': user,
        'token': token,
    })

    # Create the email message
    msg = EmailMessage(
        subject=subject,
        body=text_message,
        from_email='noreply@example.com',
        to=[user.email],
    )
    msg.content_subtype = 'html'
    msg.send()


def generate_password_reset_token(user):
    # Generate a random string of 32 hexadecimal characters
    token = secrets.token_hex(16)

    # Save the token in the user's profile
    user.password_reset_token = token
    user.save()

    return token


def register_view(request):
    if request.method == 'POST':
        # Get the form data
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        user_type = request.POST['user_type']
        username = request.POST['username']
        password = request.POST['password']

        # Create the groups if they don't already exist
        teacher_admins_group, created = Group.objects.get_or_create(name='teachers_admins')
        students_group, created = Group.objects.get_or_create(name='students')

        # Check if email or username already exists
        user_by_email = User.objects.filter(email=email).first()
        user_by_username = User.objects.filter(username=username).first()

        # If email and username don't exist, create a new user
        if user_by_email is None and user_by_username is None:
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )
            user.save()
            type_of_user = UserType(user_type=user_type)
            type_of_user.save()

            # Add the user to the appropriate group based on their user type
            if user_type == 'student':
                students_group.user_set.add(user)
            elif user_type == 'teacher_administrator':
                teacher_admins_group.user_set.add(user)

            user = authenticate(request, username=username, password=password)
            login(request, user)
            # Redirect to a success page.
            return redirect('/')
        else:
            error_message = ""
            if user_by_email is not None:
                error_message += "Email already exists. "
            if user_by_username is not None:
                error_message += "Username already exists."
            return render(request, 'register.html', {'error': error_message})
    else:
        if request.user.is_authenticated:
            # Redirect to a success page.
            return redirect('/')
        else:
            return render(request, 'register.html')
