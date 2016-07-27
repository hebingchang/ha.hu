from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.utils.html import strip_tags
from django.core.files.base import ContentFile
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.utils import timezone

from .forms import LoginForm, SignupForm
from . import models, cache
from .models import Question, Answer, Vote, U2URelationship, ContentImage
from .tasks import new_feed, new_follow, delete_follow
from hahu.settings import CACHE_CONTENT_LENGTH

from PIL import Image


@login_required
@require_GET
def index(request):
    return render(request, 'index.html', {})


@login_required
@require_GET
def index_feeds(request):
    cur_user = request.user
    feeds = cache.get_feeds(cur_user)
    is_signed = (cur_user.profile.sign_time == timezone.now().date())
    return JsonResponse(dict(cur_user=cur_user.username, feeds=feeds, is_signed=is_signed))


@login_required
@require_POST
def sign(request):
    user = request.user
    user.profile.sign_time = timezone.now().date()
    user.profile.points += 1
    user.profile.save()
    return redirect('/')


@require_GET
def profile(request, username):
    cur_user = request.user
    user = get_object_or_404(User, username=username)
    votes = Vote.objects.filter(from_user=user)
    questions = Question.objects.filter(from_user=user)
    answers = Answer.objects.filter(from_user=user)
    is_superuser = cur_user.is_superuser
    relationship = None
    if cur_user != user:
        relationship = U2URelationship.objects.filter(from_user=cur_user, to_user=user).first()
    return render(request, 'profile.html',
                  dict(user=user, profile=user.profile, cur_user=cur_user, relationship=relationship,
                       is_superuser=is_superuser, questions=questions, answers=answers, votes=votes))


@require_GET
def question(request, question_id):
    cur_user = request.user
    ques = get_object_or_404(Question, id=question_id)
    return render(request, 'question.html',
                  dict(question=ques, cur_user=cur_user))


@login_required
def new_question(request):
    cur_user = request.user
    if request.method == 'GET':
        return render(request, 'new_question.html', dict(cur_user=cur_user))

    title = request.POST.get('title', '')
    content = request.POST.get('content', '')
    print(content)
    ques = Question(from_user=cur_user, title=title, content=content)
    ques.save()
    new_feed.delay(
        user_id=cur_user.id,
        follower_names=cur_user.profile.follower_names,
        feed_id=str(ques.id), feed=dict(
            event_type='question',
            title=title,
            question_id=str(ques.id),
            content=strip_tags(content)[:CACHE_CONTENT_LENGTH],
            create_time=ques.create_time.timestamp(),
            username=cur_user.username,
            avatar=cur_user.profile.avatar.url,
            feed_id=str(ques.id)
        )
    )

    return redirect('/questions/{}'.format(ques.id))


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
    type = request.POST.get('type', '')
    cur_user = request.user
    if type == 'up':
        to_answer = get_object_or_404(Answer, id=request.POST.get('to_answer', ''))
        vote, created = Vote.objects.get_or_create(from_user=cur_user, to_answer=to_answer)
        question = vote.to_answer.from_question

        if created:
            new_feed.delay(
                user_id=cur_user.id,
                follower_names=cur_user.profile.follower_names,
                feed_id=str(vote.id), feed=dict(
                    event_type='vote',
                    title=question.title,
                    question_id=str(question.id),
                    content=strip_tags(to_answer.content)[:CACHE_CONTENT_LENGTH],
                    create_time=vote.create_time.timestamp(),
                    username=cur_user.username,
                    avatar=cur_user.profile.avatar.url,
                    feed_id=str(vote.id)
                )
            )
    if type == 'down':
        to_answer = get_object_or_404(Answer, id=request.POST.get('to_answer', ''))
        try:
            vote = Vote.objects.get(from_user=cur_user, to_answer=to_answer)
        except Exception as e:
            return JsonResponse(dict(vote_num=to_answer.vote_num))
        vote.delete()

    return JsonResponse(dict(vote_num=to_answer.vote_num))


@login_required
@require_POST
def follow(request):
    cur_user = request.user
    to_user = get_object_or_404(User, username=request.POST.get('to_user', ''))
    success = models.follow(cur_user, to_user)
    if success:
        new_follow.delay(from_user_id=cur_user.username, to_user_id=to_user.username)
    else:
        U2URelationship.objects.get(from_user=cur_user, to_user=to_user).delete()
        success = True
        delete_follow.delay(from_user_id=cur_user.username, to_user_id=to_user.username)

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
    ques = get_object_or_404(Question, id=question_id)

    if request.method == 'GET':
        return render(request, 'new_answer.html', dict(cur_user=cur_user, question=ques))
    if request.method == 'POST':
        content = request.POST.get('answer-content', '')
        answer = Answer(from_question=ques, from_user=cur_user, content=content)
        answer.save()

        new_feed.delay(
            user_id=cur_user.id,
            follower_names=cur_user.profile.follower_names,
            feed_id=str(answer.id), feed=dict(
                event_type='answer',
                title=ques.title,
                question_id=str(ques.id),
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
    cache.delete_feed(feed_id=answer_id, user_id=a.from_user.username)
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
    answers = Answer.objects.all()
    return render(request, 'discover.html',
                  dict(questions=questions, answers=answers))


@login_required
@require_POST
def search(request):
    content = request.POST.get('search', '')
    users = User.objects.filter(username__icontains=content)
    questions = Question.objects.filter(Q(title__icontains=content) | Q(content__icontains=content))
    answers = Answer.objects.filter(content__icontains=content)
    return render(request, 'search.html',
                  dict(users=users, questions=questions, answers=answers))


@login_required
@require_POST
def upload(request):
    content_image = ContentImage()
    image = request.FILES.get('image', '')
    if image:
        content_image.img.save(image.name, ContentFile(image.read()))
        content_image.save()
        abs_url = content_image.img.url

        im = Image.open(abs_url)
        w, h = im.size
        if w > 700:
            im.thumbnail((700, h * 700 / w))
        im.save(abs_url)
        abs_url = '/' + abs_url

        return HttpResponse(
            "<script>top.$('.mce-btn.mce-open').parent().find('.mce-textbox')"
            ".val('%s').closest('.mce-window').find('.mce-primary').click();</script>" % abs_url)
