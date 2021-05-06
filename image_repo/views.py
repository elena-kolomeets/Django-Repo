import os

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password, ValidationError
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import IntegrityError
from django.shortcuts import redirect, render
import requests

from .forms import ImageForm
from .models import Image


def homepage(request):
    """Homepage view"""
    return render(request, 'image_repo/homepage.html')


def user_sign_up(request):
    """User Sign up view"""
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
                                        'error': 'Username is already used. Please choose another one.'}, status=401)
            except ValidationError:
                return render(request, 'image_repo/user_sign_up.html', {'form': UserCreationForm(),
                                    'error': 'Invalid username or password. Please choose another one.'}, status=401)
        else:
            return render(request, 'image_repo/user_sign_up.html', {'form': UserCreationForm(),
                                                              'error': 'Passwords do not match.'}, status=401)


def user_sign_in(request):
    """User Sign in view"""
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
                                                'error': 'Given username or password is incorrect.'}, status=401)


def user_sign_out(request):
    """User Sign out view"""
    # adding a POST request check to disable automatic
    # preload of url in the browsers (which logs users out)
    if request.method == 'POST':
        logout(request)
        return redirect('homepage')


@login_required(login_url='homepage')
def repo(request):
    """User Image Repo view"""
    # open sign up page
    if request.method == 'GET':
        # pass all user's images and data to the template
        images = Image.objects.filter(user=request.user).order_by('id').reverse()
        # limit number of uploads to 5
        if len(images) >= 5:
            return render(request, 'image_repo/repo.html', {'images': images})
        return render(request, 'image_repo/repo.html', {'form': ImageForm(), 'images': images})
    else:  # upload an image (POST method)
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # get the uploaded image from the form and save all data to the database
                file = form.cleaned_data.get('image')
                # analyze image with Azure Computer Vision API
                result = azure_cv_api(file)
                colors = ''
                description = ''
                tags = ''
                if result is not None:
                    colors = result['colors']
                    description = result['description'].capitalize()
                    tags = result['tags']
                image_object = Image.objects.create(
                    image=file,
                    user=request.user,
                    description=description,
                    tags=tags,
                    colors=colors
                )
                image_object.save()
                # pass all user's images and data to the template
                images = Image.objects.filter(user=request.user).order_by('id').reverse()
                # limit number of uploads to 5
                if len(images) >= 5:
                    return render(request, 'image_repo/repo.html', {'images': images})
                return render(request, 'image_repo/repo.html', {'images': images, 'form': ImageForm()})
            except:
                return render(request, 'image_repo/repo.html', {'form': ImageForm(),
                                                                'error': 'Some error occurred. Kindly try again.'})


def azure_cv_api(img):
    """Helper func to call Azure Computer Vision API from repo view"""
    api_key = os.environ['AZURE_CV_KEY']
    endpoint = os.environ['AZURE_CV_ENDPOINT']
    req_url = endpoint + "vision/v3.2/analyze"
    headers = {'Ocp-Apim-Subscription-Key': api_key,
               'Content-Type': 'application/octet-stream'}
    params = {'visualFeatures': 'Description,Color'}
    try:
        response = requests.post(req_url, headers=headers, params=params, data=img)
        response.raise_for_status()
        results = response.json()
        description = results['description']['captions'][0]['text']+'.'
        tags = '#'+' #'.join(results['description']['tags'])
        colors = ' '.join(results['color']['dominantColors']).lower()
        result_dict = dict()
        result_dict['description'] = description
        result_dict['tags'] = tags
        result_dict['colors'] = colors
        return result_dict
    except Exception as e:
        print(e)
