from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render


def login_view(request):
    if request.method == 'POST':
        # Get the username and password from the form
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        # If the user is authenticated, log them in
        if user is not None:
            login(request, user)
            # Redirect to the create_quiz page
            return redirect('create_quiz')

        else:
            # Return an error message
            return render(request, 'loginpage.html', {'error': 'Invalid login'})

    else:
        if request.user.is_authenticated:
            # Redirect to the create_quiz page
            return redirect('create_quiz')

        else:
            # Display the login form
            return render(request, 'loginpage.html')


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
        first_name = escape(request.POST['first_name'])
        last_name = escape(request.POST['last_name'])
        email = escape(request.POST['email'])
        phone = escape(request.POST['phone'])
        zip_code = escape(request.POST['zip_code'])
        user_type = escape(request.POST['user_type'])
        date_of_birth = escape(request.POST['date_of_birth'])
        password = escape(request.POST['password'])
        user = User.objects.filter(email=email).first()
        if user is None:
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                zip_code=zip_code,
                user_type=user_type,
                date_of_birth=date_of_birth,
                password=password
            )
            user.save()
            user = authenticate(request, email=email, password=password)
            login(request, user)
            # Redirect to a success page.
            return redirect('/success')
        else:
            # Return an 'email already exists' error message.
            return render(request, 'register.html', {'error': 'Email already exists'})
    else:
        if request.user.is_authenticated:
            # Redirect to a success page.
            return redirect('/success')
        else:
            return render(request, 'register.html')
