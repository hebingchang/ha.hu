from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from .forms import LoginForm, SignupForm
from .models import create_user

from .models import Question, Answer, Vote, newest_events


@login_required
@require_GET
def index(request):
    cur_user = request.user
    event_objs = newest_events(cur_user, 1000)

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


@require_GET
def profile(request, username):
    if request.method == 'GET':
        cur_user = request.user
        user = get_object_or_404(User, username=username)
        return render(request, 'profile.html',
                      dict(user=user, profile=user.profile, cur_user=cur_user))
    else:
        pass


@require_GET
def question(request, question_id):
    cur_user = request.user
    question = get_object_or_404(Question, id=question_id)
    return render(request, 'question.html',
                  dict(question=question, cur_user=cur_user))


@login_required
@require_POST
def new_question(request):
    cur_user = request.user
    title = request.POST.get('title', '')
    content = request.POST.get('content', '')

    q = Question(from_user=cur_user, title=title, content=content)
    q.save()

    return redirect('/question/{}'.format(q.id))


@login_required
@require_POST
def vote(request):
    cur_user = request.user
    to_user = get_object_or_404(User, username=request.POST.get('to_user', ''))

    Vote(from_user=cur_user, to_user=to_user).save()

    return HttpResponse('')


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
