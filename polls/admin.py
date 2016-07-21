from django.contrib import admin
from .models import *

admin.site.register([Profile, Question, Answer, Comment, Vote, U2URelationship, Chat, Message])
