import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

class QuestionModelTests(TestCase):
    def was_published_recently_test(self, time, boolean=True):
        question = Question(publish_date=time)

        self.assertIs(question.was_published_recently(), boolean)


    def test_was_published_recently_with_future_question(self):
        """
        was_publish_recently() returns False for questions whose publish_date
        is in the future
        """
        self.was_published_recently_test(timezone.now() + datetime.timedelta(days=30), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions who publish_date
        is older than one day
        """
        self.was_published_recently_test(timezone.now() - datetime.timedelta(days=30), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns true for questions who publish_date
        is within the last day
        """
        self.was_published_recently_test(timezone.now() - datetime.timedelta(hours = 12))

def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)

    return Question.objects.create(question_text=question_text, publish_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("polls:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a publish_date in the past are displayed on the index page.
        """
        create_question(question_text="Past question.", days=-30)

        response = self.client.get(reverse("polls:index"))

        self.assertQuerysetEqual(
                response.context["latest_question_list"],
                ["<Question: Past question.>"]
                )

    def test_future_question(self):
        """
        Questions with a publish_date in the future aren't displayed on the index page.
        """
        create_question(question_text="Future question.", days=30)

        response = self.client.get(reverse("polls:index"))

        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"],[])

    def test_future_and_past_question(self):
        """
        If both past and future questions exist, only past questions displayed
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)

        response = self.client.get(reverse("polls:index"))

        self.assertQuerysetEqual(
                response.context["latest_question_list"],
                ["<Question: Past question.>"]
                )

    def test_two_past_questions(self):
        """
        Displays multiple past questions
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Past question 2.", days=-31)

        response = self.client.get(reverse("polls:index"))

        self.assertQuerysetEqual(
                response.context["latest_question_list"],
                ["<Question: Past question.>", "<Question: Past question 2.>"]
                )

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a publish_date in the future
        returns a 404
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("polls:detail", args=(future_question.id,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_future_question(self):
        """
        The detail view of a question with a publish_date in the past
        displays the questions's text.
        """
        past_question = create_question(question_text="Past question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, past_question.question_text)
