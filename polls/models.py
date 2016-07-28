from django.db import models, connection
from django.utils import timezone
from django.utils.html import strip_tags
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from imagekit.models import ProcessedImageField
from datetime import datetime
from django.conf import settings
from django.contrib.sessions.models import Session
from django.contrib.auth.signals import user_logged_in

from hahu.settings import CACHE_CONTENT_LENGTH

import uuid
import logging

logger = logging.getLogger(__name__)


def _content_file_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.inner_user.username, ext)
    return 'static/avatars/' + filename


class Profile(models.Model):
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2

    free_time = models.DateTimeField(default=timezone.now)
    points = models.IntegerField(default=0)
    gender = models.IntegerField(default=0)
    inner_user = models.OneToOneField(User)
    first_name = models.CharField(max_length=10, default='')
    last_name = models.CharField(max_length=10, default='')
    avatar = models.ImageField(upload_to=_content_file_name, default='static/images/anonymous.jpg')
    self_intro = models.CharField(max_length=150, default='此用户太懒了，并没有填写个人介绍...')
    sign_time = models.DateField(default=datetime(1970, 1, 1))

    def __str__(self):
        return 'username: {}, nickname: {}, points: {}, gender: {}' \
            .format(self.inner_user.username, self.nickname, self.points, self.gender)

    @property
    def followers(self):
        return list(map(lambda r: r.from_user, U2URelationship
                        .objects.select_related('from_user')
                        .filter(to_user=self.inner_user, relationship=0).all()))

    @property
    def follower_names(self):
        return list(map(lambda r: r.from_user.username, U2URelationship
                        .objects.select_related('from_user')
                        .filter(to_user=self.inner_user, relationship=0).all()))

    @property
    def followees(self):
        return list(map(lambda r: r.to_user, U2URelationship
                        .objects.select_related('to_user')
                        .filter(from_user=self.inner_user, relationship=0).all()))

    def ban(self, days=1):
        self.free_time = timezone.now() + timezone.timedelta(days=days)


class UserSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    session = models.ForeignKey(Session)


def user_logged_in_handler(sender, request, user, **kwargs):
    UserSession.objects.get_or_create(user=user, session_id=request.session.session_key)


user_logged_in.connect(user_logged_in_handler)


def create_user(username, email, password, **kwargs):
    inner_user = User.objects.create_user(username, email, password)
    user_profile = Profile(inner_user=inner_user, **kwargs)
    user_profile.save()
    logger.info('create user', user_profile)
    return inner_user


def follow(from_user, user):
    if not user or from_user == user:
        return False

    _, created = U2URelationship.objects.get_or_create(from_user=from_user, to_user=user)
    return created


class Question(models.Model):
    __tablename__ = 'question'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100, default='')
    content = models.TextField(default='')
    create_time = models.DateTimeField(default=timezone.now)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)

    class Meta:
        ordering = ('-create_time',)

    def __str__(self):
        return 'title: {}, content: {}, create_time: {}, from_username: {}' \
            .format(self.title, self.content, self.create_time, self.from_user.username)

    @property
    def answers(self):
        return sorted(self.answer_set.all(), key=lambda x: -x.vote_num)


class Topic(models.Model):
    name = models.CharField(max_length=10, default='')
    descriptor = models.TextField(default='')
    questions = models.ManyToManyField(Question, related_name='topics')


class Answer(models.Model):
    __tablename__ = 'answer'

    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    content = models.TextField(default='')
    from_user = models.ForeignKey(User, blank=True, on_delete=models.CASCADE)
    from_question = models.ForeignKey(Question, blank=True, on_delete=models.CASCADE, db_index=True)
    create_time = models.DateTimeField(default=timezone.now)
    edit_time = models.DateTimeField(default=timezone.now)

    @property
    def vote_num(self):
        return Vote.objects.filter(choice=0, to_answer=self).count()


class Comment(models.Model):
    content = models.CharField(max_length=100, default='')
    from_user = models.ForeignKey(User, related_name='user_comments')
    from_answer = models.ForeignKey(Answer, related_name='comments')


class Vote(models.Model):
    __tablename__ = 'vote'

    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    # TODO: CharField | Choice
    # Vote up, Vote down, Thanks, Helpless
    create_time = models.DateTimeField(default=timezone.now)
    choice = models.IntegerField(default=0)
    to_answer = models.ForeignKey(Answer, blank=True, on_delete=models.CASCADE, db_index=True)
    from_user = models.ForeignKey(User, blank=True, on_delete=models.CASCADE, db_index=True)

    unique_together = ('to_answer', 'from_user')


def newest_events(user, num=10):
    followees = user.profile.followees
    cnt = len(followees)
    if cnt == 0:
        return []
    query_sign = '=' if cnt == 1 else 'IN'
    followees_id_str = '(%s)' % ', '.join(map(lambda x: str(x.id), followees))

    with connection.cursor() as c:
        event_types = ['question', 'answer', 'vote']
        single_query_sql_template = \
            """
            SELECT id, create_time, from_user_id, "{}" AS table_name
            FROM polls_{}
            WHERE from_user_id {} {}
            """

        union_query_sql = '\nUNION\n'.join(
            [single_query_sql_template.format(t, t, query_sign, followees_id_str) for t in event_types])

        raw_sql = union_query_sql + \
                  """
                  ORDER BY create_time DESC
                  LIMIT {}
                  """.format(num)

        print(raw_sql)

        logger.info('raw sql', raw_sql)
        c.execute(raw_sql)

        results = c.fetchall()

    events = []
    for r in results:
        event_id, event_type = r[0], r[-1]
        events.append(({'question': Question,
                        'answer': Answer,
                        'vote': Vote,
                        })[event_type].objects.get(id=event_id))

    return events


def get_self_feeds(user, start=0, end=100):
    if start >= end:
        return []

    with connection.cursor() as c:
        event_types = ['question', 'answer', 'vote']
        single_query_sql_template = \
            """
            SELECT id, create_time, from_user_id, "{}" AS table_name
            FROM polls_{}
            WHERE from_user_id = {}
            """

        union_query_sql = '\nUNION\n'.join(
            [single_query_sql_template.format(t, t, user.id) for t in event_types])

        raw_sql = union_query_sql + \
                  """
                  ORDER BY create_time DESC
                  LIMIT {}, {}
                  """.format(start, end)

        print(raw_sql)

        logger.info('raw sql', raw_sql)
        c.execute(raw_sql)

        results = c.fetchall()

    feeds = []

    for r in results:
        event_id, event_type = r[0], r[-1]
        event = ({'question': Question,
                  'answer': Answer,
                  'vote': Vote,
                  })[event_type].objects.get(id=event_id)

        feed = dict(event_type=event_type,
                    feed_id=str(event.id),
                    create_time=event.create_time.timestamp(),
                    username=event.from_user.username,
                    avatar=event.from_user.profile.avatar.url)

        if event_type == 'question':
            feed.update(title=event.title,
                        question_id=str(event.id),
                        content=strip_tags(event.content)[:CACHE_CONTENT_LENGTH])
        elif event_type == 'answer':
            feed.update(title=event.from_question.title,
                        question_id=str(event.from_question.id),
                        content=strip_tags(event.content)[:CACHE_CONTENT_LENGTH])
        elif event_type == 'vote':
            feed.update(title=event.to_answer.from_question.title,
                        question_id=str(event.to_answer.from_question.id),
                        content=event.to_answer.content[:CACHE_CONTENT_LENGTH])

        feeds.append(feed)

    return feeds


def get_feeds(user, start=0, end=100):
    if start >= end:
        return []

    followees = user.profile.followees
    cnt = len(followees)
    if cnt == 0:
        return []
    query_sign = '=' if cnt == 1 else 'IN'
    followees_id_str = '(%s)' % ', '.join(map(lambda x: str(x.id), followees))

    with connection.cursor() as c:
        event_types = ['question', 'answer', 'vote']
        single_query_sql_template = \
            """
            SELECT id, create_time, from_user_id, "{}" AS table_name
            FROM polls_{}
            WHERE from_user_id {} {}
            """

        union_query_sql = '\nUNION\n'.join(
            [single_query_sql_template.format(t, t, query_sign, followees_id_str) for t in event_types])

        raw_sql = union_query_sql + \
                  """
                  ORDER BY create_time DESC
                  LIMIT {}, {}
                  """.format(start, end)

        print(raw_sql)

        logger.info('raw sql', raw_sql)
        c.execute(raw_sql)

        results = c.fetchall()

    feeds = []

    for r in results:
        event_id, event_type = r[0], r[-1]
        event = ({'question': Question,
                  'answer': Answer,
                  'vote': Vote,
                  })[event_type].objects.get(id=event_id)

        feed = dict(event_type=event_type,
                    feed_id=str(event.id),
                    create_time=event.create_time.timestamp(),
                    username=event.from_user.username,
                    avatar=event.from_user.profile.avatar.url)

        if event_type == 'question':
            feed.update(title=event.title,
                        question_id=str(event.id),
                        content=strip_tags(event.content)[:CACHE_CONTENT_LENGTH])
        elif event_type == 'answer':
            feed.update(title=event.from_question.title,
                        question_id=str(event.from_question.id),
                        content=strip_tags(event.content)[:CACHE_CONTENT_LENGTH])
        elif event_type == 'vote':
            feed.update(title=event.to_answer.from_question.title,
                        question_id=str(event.to_answer.from_question.id),
                        content=event.to_answer.content[:CACHE_CONTENT_LENGTH])

        feeds.append(feed)

    return feeds


class U2URelationship(models.Model):
    # TODO: CharField | Choice
    # Follow, Block
    relationship = models.IntegerField(default=0, db_index=True)
    from_user = models.ForeignKey(User, blank=True, related_name='to_user_relationship', db_index=True)
    to_user = models.ForeignKey(User, blank=True, related_name='from_user_relationship', db_index=True)


class Chat(models.Model):
    from_user = models.ForeignKey(User, related_name='chat_from_user', db_index=True)
    to_user = models.ForeignKey(User, related_name='chat_to_user', db_index=True)


class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', db_index=True)
    create_time = models.DateTimeField(default=timezone.now)
    direction = models.SmallIntegerField(default=0)


def _image_file_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (str(instance.id), ext)
    return 'static/uploads/' + filename


class ContentImage(models.Model):
    img = ProcessedImageField(upload_to=_image_file_name,
                              format='JPEG',
                              options={'quality': 60})
