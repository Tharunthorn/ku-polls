import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
import datetime

from .models import Question


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )

class QuestionModelTests(TestCase):
    def create_question_with_dates(self, pub_date, end_date=None):
        return Question.objects.create(question_text="Sample question", pub_date=pub_date, end_date=end_date)

    def test_is_published_with_future_pub_date(self):
        """Cannot be published if the pub_date is in the future."""
        future_date = timezone.now() + datetime.timedelta(days=1)
        question = self.create_question_with_dates(pub_date=future_date)
        self.assertIs(question.is_published(), False)

    def test_is_published_with_default_pub_date(self):
        """Is published if the pub_date is now."""
        now = timezone.now()
        question = self.create_question_with_dates(pub_date=now)
        self.assertIs(question.is_published(), True)

    def test_is_published_with_past_pub_date(self):
        """Is published if the pub_date is in the past."""
        past_date = timezone.now() - datetime.timedelta(days=1)
        question = self.create_question_with_dates(pub_date=past_date)
        self.assertIs(question.is_published(), True)

    def test_can_vote_before_pub_date(self):
        """Cannot vote if the current date/time is before the pub_date."""
        future_date = timezone.now() + datetime.timedelta(days=1)
        question = self.create_question_with_dates(pub_date=future_date)
        self.assertIs(question.can_vote(), False)

    def test_can_vote_after_end_date(self):
        """Cannot vote if the end_date is in the past."""
        past_end_date = timezone.now() - datetime.timedelta(days=1)
        pub_date = timezone.now() - datetime.timedelta(days=2)
        question = self.create_question_with_dates(pub_date=pub_date, end_date=past_end_date)
        self.assertIs(question.can_vote(), False)

    def test_can_vote_within_date_range(self):
        """Can vote if the current date/time is between the pub_date and end_date."""
        future_end_date = timezone.now() + datetime.timedelta(days=1)
        pub_date = timezone.now() - datetime.timedelta(days=1)
        question = self.create_question_with_dates(pub_date=pub_date, end_date=future_end_date)
        self.assertIs(question.can_vote(), True)

    def test_can_vote_after_pub_date_no_end_date(self):
        """Can vote anytime after pub_date if end_date is None."""
        pub_date = timezone.now() - datetime.timedelta(days=1)
        question = self.create_question_with_dates(pub_date=pub_date)
        self.assertIs(question.can_vote(), True)
