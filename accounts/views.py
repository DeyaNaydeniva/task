from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


def auth_page(request):
    return render(request, 'accounts/auth.html', {'active_tab': 'signin'})


def signin_view(request):
    if request.method != 'POST':
        return redirect('accounts:auth')

    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')
    remember = request.POST.get('remember')

    errors = []

    try:
        user_obj = User.objects.get(email=email)
        username = user_obj.username
    except User.DoesNotExist:
        username = None

    user = authenticate(request, username=username, password=password) if username else None

    if user is None:
        errors.append('Invalid email or password.')
        return render(request, 'accounts/auth.html', {
            'active_tab': 'signin',
            'signin_errors': errors,
            'signin_email': email,
        })

    login(request, user)
    if not remember:
        request.session.set_expiry(0)

    return redirect('accounts:auth')


def signup_view(request):
    if request.method != 'POST':
        return redirect('accounts:auth')

    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')
    confirm = request.POST.get('confirm', '')

    errors = []

    if not first_name:
        errors.append('First name is required.')
    if not last_name:
        errors.append('Last name is required.')
    if not email or '@' not in email:
        errors.append('A valid email is required.')
    elif User.objects.filter(email=email).exists():
        errors.append('An account with this email already exists.')
    if len(password) < 8:
        errors.append('Password must be at least 8 characters.')
    elif password != confirm:
        errors.append("Passwords don't match.")

    if errors:
        return render(request, 'accounts/auth.html', {
            'active_tab': 'signup',
            'signup_errors': errors,
            'signup_data': {'first_name': first_name, 'last_name': last_name, 'email': email},
        })

    username = email.split('@')[0]
    base = username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f'{base}{counter}'
        counter += 1

    User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )

    return render(request, 'accounts/auth.html', {
        'active_tab': 'signup',
        'show_success': True,
    })
