from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .forms import LoginForm, SignupForm
from .models import create_user

from .models import Question, Answer, Vote, newest_events


def index(request):
    if not request.user:
        return redirect('/accounts/login/')

    user = request.user
    event_objs = newest_events(user, 1000)

    events = []
    for o in event_objs:
        e = dict(create_time=o.create_time, from_user_nickname=o.from_user.username)
        if type(o) == Question:
            e.update(event_type='question', title=o.title, conent=o.content)
        elif type(o) == Answer:
            e.update(event_type='answer', content=o.content, question_title=o.from_question.title)
        elif type(o) == Vote:
            pass

        events.append(e)

    return render(request, 'index.html', {'events': events})


def profile(request, username):
    cur_user = request.user
    user = get_object_or_404(User, username=username)
    return render(request, 'profile.html',
                  dict(username=user.username, profile=user.profile, cur_username=cur_user.username))


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html', {})
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return redirect('/')
            else:
                return render(request, 'login.html', {'password_is_wrong': True})
        else:
            return render(request, 'login.html', {})


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {})
    else:
        form = SignupForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username', '')
            email = request.POST.get('email', '')
            password = request.POST.get('password', '')
            user = create_user(username, email, password)
            if user is not None:
                return redirect('/accounts/login/')
            else:
                return render(request, 'signup.html', {'error': True})
        else:
            return render(request, 'signup.html', {})
