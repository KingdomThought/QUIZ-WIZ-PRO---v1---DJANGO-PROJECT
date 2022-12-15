from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils.html import escape

from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views.decorators.csrf import csrf_protect


@csrf_protect
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is None:
                messages.error(request, "Invalid username or password.")
                return redirect('login_view')
            else:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}")
                # Return the user to the main dashboard page
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login_view')
    form = AuthenticationForm()
    return render(request=request,
                  template_name="loginpage.html",
                  context={"form": form})


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
        # phone = request.POST['phone']
        # zip_code = request.POST['zip_code']
        # user_type = request.POST['user_type']
        username = request.POST['username']
        # date_of_birth = request.POST['date_of_birth']
        password = request.POST['password']

        # Check if email already exists
        user = User.objects.filter(email=email).first()

        # If email doesn't exist, create a new user
        if user is None:
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                # phone=phone,
                # zip_code=zip_code,
                # user_type=user_type,
                username=username,
                # date_of_birth=date_of_birth,
                password=password
            )
            user.save()
            user = authenticate(request, email=email, password=password)
            login(request, user)
            # Redirect to a success page.
            return redirect('register_view')
        else:
            # Return an 'email already exists' error message.
            return render(request, 'register.html', {'error': 'Email already exists'})
    else:
        if request.user.is_authenticated:
            # Redirect to a success page.
            return redirect('register_view')
        else:
            return render(request, 'register.html')