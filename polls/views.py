from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.files.base import ContentFile

from .forms import LoginForm, SignupForm
from . import models
from .models import Question, Answer, Vote


@login_required
@require_GET
def index(request):
    cur_user = request.user
    event_objs = models.newest_events(cur_user, 1000)

    events = list(map(lambda e: (type(e).__tablename__, e), event_objs))

    return render(request, 'index.html', dict(cur_user=cur_user, events=events))


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
def new_question(request):
    cur_user = request.user
    if request.method == 'GET':
        return render(request, 'new_question.html', dict(cur_user=cur_user))

    title = request.POST.get('title', '')
    content = request.POST.get('content', '')
    q = Question(from_user=cur_user, title=title, content=content)
    q.save()
    return redirect('/questions/{}'.format(q.id))


@login_required
@require_POST
def vote(request):
    cur_user = request.user

    to_answer = get_object_or_404(Answer, id=request.POST.get('to_answer', ''))
    Vote.objects.get_or_create(from_user=cur_user, to_answer=to_answer)

    return JsonResponse(dict(vote_num=to_answer.vote_num))


@login_required
@require_POST
def follow(request):
    cur_user = request.user
    to_user = get_object_or_404(User, username=request.POST.get('to_user', ''))
    success = models.follow(cur_user, to_user)

    return JsonResponse(dict(success=success))


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
            user = models.create_user(username, email, password)
            if user is not None:
                return redirect('/accounts/login/')
            else:
                return render(request, 'signup.html', {'error': True})
        else:
            return render(request, 'signup.html', {})


@require_GET
def getinfo(request):
    return JsonResponse(dict(username=request.user.username))


@login_required
def settings(request):
    if request.method == 'GET':
        cur_user = request.user
        return render(request, 'settings.html', dict(cur_user=cur_user))
    else:
        cur_user = request.user
        cur_user.password = cur_user.password if request.POST.get('password', '') == '' else request.POST.get(
            'password', '')
        cur_user.email = request.POST.get('email', '')
        cur_user.profile.last_name = request.POST.get('last_name', '')
        cur_user.profile.first_name = request.POST.get('first_name', '')
        cur_user.profile.gender = int(request.POST.get('gender', ''))
        avatar = request.FILES.get('avatar', '')
        if avatar:
            cur_user.profile.avatar.save(avatar.name, ContentFile(avatar.read()))
        cur_user.save()
        cur_user.profile.save()
        return redirect('/settings/')


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/')


def new_answer(request, question_id):
    cur_user = request.user
    question = get_object_or_404(Question, id=question_id)

    if request.method == 'GET':
        return render(request, 'new_answer.html', dict(cur_user=cur_user, question=question))
    if request.method == 'POST':
        content = request.POST.get('answer-content', '')
        Answer(from_question=question, from_user=cur_user, content=content).save()
        return redirect('/questions/{}/'.format(question_id))
