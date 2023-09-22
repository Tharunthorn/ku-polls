import datetime

from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.contrib.auth.models import User


class Question(models.Model):
    """
    Represents a single poll question.
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    end_date = models.DateTimeField('end date', null=True, blank=True)

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    @admin.display(
        boolean=True,
        ordering='pub_date',
        description='Published recently?',
    )
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def __str__(self):
        return self.question_text

    def is_published(self):
        """
        Determines if the question is published.
        """
        return timezone.now() >= self.pub_date

    def can_vote(self):
        now = timezone.now()
        return self.pub_date <= now and (self.end_date is None or now <= self.end_date)


class Choice(models.Model):
    """
    Choice model that act as options for Question
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    #votes = models.IntegerField(default=0)

    @property
    def votes(self):
        """
        Count the votes for this choice.
        """
        #count = Vote.objects.filter(choice=self).count()
        return self.vote_set.count()

    def __str__(self):
        """
        Displaying choices for the question.
        """
        return self.choice_text

class Vote(models.Model):
    """
    Records a Vote of a Choice by a User.
    """
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
