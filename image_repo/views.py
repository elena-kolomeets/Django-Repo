from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password, ValidationError
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import IntegrityError
from django.shortcuts import redirect, render


def homepage(request):
    return render(request, 'image_repo/base.html')


def user_sign_up(request):
    if request.method == 'GET':  # open sign up page
        return render(request, 'image_repo/user_sign_up.html', {'form': UserCreationForm()})
    else:
        # create a new user with a built-in model
        if request.POST.get('password1') == request.POST.get('password2'):
            try:
                UnicodeUsernameValidator(request.POST.get('username'))
                validate_password(request.POST.get('password1'))
                user = User.objects.create_user(request.POST.get('username'), password=request.POST.get('password1'))
                user.save()
                login(request, user)
                # if user signed up, log him in and show the repo
                return redirect('repo')
            except IntegrityError:
                return render(request, 'image_repo/user_sign_up.html', {'form': UserCreationForm(),
                                                    'error': 'Username is already used. Please choose another one.'})
            except ValidationError:
                return render(request, 'image_repo/user_sign_up.html', {'form': UserCreationForm(),
                                                'error': 'Invalid username or password. Please choose another one.'})
        else:
            return render(request, 'image_repo/user_sign_up.html', {'form': UserCreationForm(),
                                                              'error': 'Passwords do not match'})


def user_sign_in(request):
    if request.method == 'GET':  # open sign in page
        return render(request, 'image_repo/user_sign_in.html', {'form': AuthenticationForm()})
    else:
        # sign in user with a built-in model
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        # if sign in successful, show the repo
        if user is not None:
            login(request, user)
            return redirect('repo')
        else:
            return render(request, 'image_repo/user_sign_in.html', {'form': AuthenticationForm(),
                                                'error': 'Given username or password is incorrect.'})


def user_sign_out(request):
    # adding a POST request check to disable automatic
    # preload of url in the browsers (which logs users out)
    if request.method == 'POST':
        logout(request)
        return redirect('homepage')


def repo(request):
    return render(request, 'image_repo/repo.html')
