from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils.html import strip_tags
from django.core.files.base import ContentFile
from django.contrib.admin.views.decorators import staff_member_required

from .forms import LoginForm, SignupForm
from . import models, cache
from .models import Question, Answer, Vote, U2URelationship
from .tasks import new_feed
from hahu.settings import CACHE_CONTENT_LENGTH


@login_required
@require_GET
def index(request):
    cur_user = request.user
    feeds = cache.get_feeds(cur_user)
    return render(request, 'index.html', dict(cur_user=cur_user, feeds=feeds))


@require_GET
def profile(request, username):
    cur_user = request.user
    user = get_object_or_404(User, username=username)
    is_superuser = cur_user.is_superuser
    relationship = None
    if cur_user != user:
        relationship = U2URelationship.objects.filter(from_user=cur_user, to_user=user).first()
    return render(request, 'profile.html',
                  dict(user=user, profile=user.profile, cur_user=cur_user, relationship=relationship,
                       is_superuser=is_superuser))


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
    question = Question(from_user=cur_user, title=title, content=content)
    question.save()
    new_feed.delay(
        user_id=cur_user.id,
        follower_names=cur_user.profile.follower_names,
        feed_id=str(question.id), feed=dict(
            event_type='question',
            title=title,
            content=strip_tags(content)[:CACHE_CONTENT_LENGTH],
            create_time=question.create_time.timestamp(),
            username=cur_user.username,
            avatar=cur_user.profile.avatar.url,
            feed_id=str(question.id)
        )
    )

    return redirect('/questions/{}'.format(question.id))


@login_required
@staff_member_required
def delete_question(request):
    question_id = int(request.POST.get('question_id', ''))
    q = get_object_or_404(Question, id=question_id)
    q.delete()
    return redirect('/')


@login_required
@require_POST
def vote(request):
    cur_user = request.user

    to_answer = get_object_or_404(Answer, id=request.POST.get('to_answer', ''))
    vote, created = Vote.objects.get_or_create(from_user=cur_user, to_answer=to_answer)

    if created:
        new_feed.delay(
            user_id=cur_user.id,
            follower_names=cur_user.profile.follower_names,
            feed_id=str(vote.id), feed=dict(
                event_type='vote',
                title=to_answer.from_question.title,
                content=strip_tags(to_answer.content)[:CACHE_CONTENT_LENGTH],
                create_time=vote.create_time.timestamp(),
                username=cur_user.username,
                avatar=cur_user.profile.avatar.url,
                feed_id=str(vote.id)
            )
        )

    return JsonResponse(dict(vote_num=to_answer.vote_num))


@login_required
@require_POST
def follow(request):
    cur_user = request.user
    to_user = get_object_or_404(User, username=request.POST.get('to_user', ''))
    success = models.follow(cur_user, to_user)
    if not success:
        U2URelationship.objects.get(from_user=cur_user, to_user=to_user).delete()
        success = True

    return JsonResponse(dict(success=success))


def login(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            return redirect('/')
        else:
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
        if request.POST.get('password', '') != '':
            cur_user.set_password(request.POST.get('password', ''))
        cur_user.email = request.POST.get('email', '')
        cur_user.profile.last_name = request.POST.get('last_name', '')
        cur_user.profile.first_name = request.POST.get('first_name', '')
        cur_user.profile.gender = int(request.POST.get('gender', ''))
        cur_user.profile.self_intro = request.POST.get('intro', '')
        avatar = request.FILES.get('avatar', '')
        if avatar:
            cur_user.profile.avatar.save(avatar.name, ContentFile(avatar.read()))
        cur_user.save()
        cur_user.profile.save()
        return redirect('/settings/')


@login_required
@require_GET
def logout(request):
    auth.logout(request)
    return redirect('/')


@login_required
def new_answer(request, question_id):
    cur_user = request.user
    question = get_object_or_404(Question, id=question_id)

    if request.method == 'GET':
        return render(request, 'new_answer.html', dict(cur_user=cur_user, question=question))
    if request.method == 'POST':
        content = request.POST.get('answer-content', '')
        answer = Answer(from_question=question, from_user=cur_user, content=content)
        answer.save()

        new_feed.delay(
            user_id=cur_user.id,
            follower_names=cur_user.profile.follower_names,
            feed_id=str(answer.id), feed=dict(
                event_type='answer',
                title=question.title,
                content=strip_tags(content)[:CACHE_CONTENT_LENGTH],
                create_time=answer.create_time.timestamp(),
                username=cur_user.username,
                avatar=cur_user.profile.avatar.url,
                feed_id=str(answer.id)
            )
        )

        return redirect('/questions/{}/'.format(question_id))


@login_required
@staff_member_required
def delete_answer(request):
    answer_id = int(request.POST.get('answer_id', ''))
    question_id = int(request.POST.get('question_id', ''))
    a = get_object_or_404(Answer, id=answer_id)
    a.delete()
    return redirect('/questions/{}/'.format(question_id))


@login_required
@staff_member_required
def deactive_user(request):
    user = request.POST.get('target_user', '')
    target_user = User.objects.get(username=user)
    target_user.is_active = not target_user.is_active
    target_user.save()
    return redirect('/profile/{}/'.format(user))


@login_required
def chat(request):
    return render(request, 'chat.html', {})


def discover(request):
    questions = Question.objects.all()
    return render(request, 'discover.html',
                  dict(questions=questions))
