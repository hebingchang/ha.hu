from django.db import models
from django.utils import timezone


class User(models.Model):
    nickname = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    register_time = models.DateTimeField(default=timezone.now())

    class Meta:
        ordering = ('register_time',)

    def __str__(self):
        return 'nickname: {}, email: {}, register_time: {}, question_count: {}' \
            .format(self.nickname, self.email, self.register_time, self.question_set.count())

    @property
    def followers(self):
        return U2URelationShip.objects.filter(to_user=self)

    @property
    def followees(self):
        # TODO:
        return U2URelationShip.objects.filter(from_user=self, relationship=0)


class Question(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='questions')


class Answer(models.Model):
    content = models.TextField(default='')
    user = models.ForeignKey(User, blank=True, on_delete=models.CASCADE, related_name='answers')


class Vote(models.Model):
    # TODO: CharField | Choice
    # Vote up, Vote down, Thanks, Helpless
    choice = models.IntegerField(default=0)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, blank=True, on_delete=models.CASCADE)


class U2URelationShip(models.Model):
    # TODO: CharField | Choice
    # Follow, Block
    relationship = models.IntegerField(default=0, db_index=True)
    from_user = models.ForeignKey(User, primary_key=True)
    to_user = models.ForeignKey(User)
