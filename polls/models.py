from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class User(models.Model):
    nickname = models.CharField(max_length=30, default='', db_index=True)
    email = models.EmailField(blank=True, db_index=True)
    register_time = models.DateTimeField(default=timezone.now)
    free_time = models.DateTimeField(default=timezone.now)
    points = models.IntegerField(default=0)

    class Meta:
        ordering = ('-register_time',)

    def __str__(self):
        return 'nickname: {}, email: {}, register_time: {}, question_count: {}' \
            .format(self.nickname, self.email, self.register_time, self.question_set.count())

    @property
    def followers(self):
        return U2URelationShip.objects.filter(to_user=self, relationship=0)

    @property
    def followees(self):
        return U2URelationShip.objects.filter(from_user=self, relationship=0)

    def ban(self, days=1):
        self.free_time = timezone.now() + timezone.timedelta(days=days)


class Question(models.Model):
    title = models.CharField(max_length=100, default='')
    content = models.TextField(default='')
    create_time = models.DateTimeField(default=timezone.now)
    from_user = models.ForeignKey(User, blank=True, on_delete=models.CASCADE, db_index=True)

    class Meta:
        ordering = ('-create_time',)

    @staticmethod
    def new_question(**kwargs):
        q = Question(**kwargs)
        q.save()
        News(event=q).save()
        return q


class Topic(models.Model):
    name = models.CharField(max_length=10, default='')
    descriptor = models.TextField(default='')
    questions = models.ManyToManyField(Question, related_name='topics')


class Answer(models.Model):
    content = models.TextField(default='')
    from_user = models.ForeignKey(User, blank=True, on_delete=models.CASCADE)
    from_question = models.ForeignKey(Question, blank=True, on_delete=models.CASCADE, db_index=True)
    create_time = models.DateTimeField(default=timezone.now)
    edit_time = models.DateTimeField(default=timezone.now)

    @staticmethod
    def new_answer(**kwargs):
        a = Answer(**kwargs)
        a.save()
        News(event=a).save()
        return a


class Comment(models.Model):
    content = models.CharField(max_length=100, default='')
    from_user = models.ForeignKey(User, related_name='user_comments')
    from_answer = models.ForeignKey(Answer, related_name='comments')
    vote_num = models.IntegerField(default=0)


class Vote(models.Model):
    # TODO: CharField | Choice
    # Vote up, Vote down, Thanks, Helpless
    create_time = models.DateTimeField(default=timezone.now)
    choice = models.IntegerField(default=0)
    to_answer = models.ForeignKey(Answer, blank=True, on_delete=models.CASCADE, db_index=True)
    from_user = models.ForeignKey(User, blank=True, on_delete=models.CASCADE, db_index=True)

    @staticmethod
    def new_vote(**kwargs):
        v = Vote(**kwargs)
        v.save()
        News(event=v).save()
        return v


class U2URelationShip(models.Model):
    # TODO: CharField | Choice
    # Follow, Block
    relationship = models.IntegerField(default=0, db_index=True)
    from_user = models.ForeignKey(User, blank=True, related_name='to_user_relationship', db_index=True)
    to_user = models.ForeignKey(User, blank=True, related_name='from_user_relationship', db_index=True)


class News(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    event = GenericForeignKey('content_type', 'object_id')

    @staticmethod
    def newest(user, num=10, page=0):
        return News.objects.all()[:10]


class Chat(models.Model):
    from_user = models.ForeignKey(User, related_name='chat_from_user', db_index=True)
    to_user = models.ForeignKey(User, related_name='chat_to_user', db_index=True)


class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', db_index=True)
    create_time = models.DateTimeField(default=timezone.now)
    direction = models.SmallIntegerField(default=0)
