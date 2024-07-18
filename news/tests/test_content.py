"""Тестирование контента через unittest."""

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from news.models import Comment, News
from news.forms import CommentForm

User = get_user_model()


class TestContent(TestCase):
    """Класс тестирования на главной странице."""

    HOME_URL = reverse('news:home')

    @classmethod
    def setUpTestData(cls):
        """Создание данных для тестирования."""
        today = datetime.today()
        all_news = []
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
            news = News(
                title=f'Новость {index}',
                text='Просто текст.',
                date=today - timedelta(days=index)
            )
            all_news.append(news)
        News.objects.bulk_create(all_news)

    def test_news_count(self):
        """Проверяем, что на домашней странице 10 новостей."""
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        news_count = object_list.count()
        self.assertEqual(news_count, settings.NEWS_COUNT_ON_HOME_PAGE)

    def test_news_order(self):
        """Проверяем сортировку новостей по времени убывания."""
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        all_dates = [news.date for news in object_list]
        sorted_dates = sorted(all_dates, reverse=True)
        self.assertEqual(all_dates, sorted_dates)


class TestDetailPage(TestCase):
    """Класс тестирования на странице новости."""

    @classmethod
    def setUpTestData(cls):
        """Создание данных для тестирования."""
        cls.news = News.objects.create(
            title='Тестовая новость', text='Просто текст.'
        )
        cls.detail_url = reverse('news:detail', args=(cls.news.id,))
        cls.author = User.objects.create(username='Комментатор')
        now = timezone.now()
        for index in range(10):
            comment = Comment.objects.create(
                news=cls.news, author=cls.author, text=f'Tекст {index}',
            )
            comment.created = now + timedelta(days=index)
            comment.save()

    def test_comments_order(self):
        """Проверяем сортировку комментариев по времени убывания."""
        response = self.client.get(self.detail_url)
        self.assertIn('news', response.context)
        news = response.context['news']
        all_comments = news.comment_set.all()
        all_timestamps = [comment.created for comment in all_comments]
        sorted_timestamps = sorted(all_timestamps)
        self.assertEqual(all_timestamps, sorted_timestamps)

    def test_anonymous_client_has_no_form(self):
        """Проверяем, что гостю не передается форма."""
        response = self.client.get(self.detail_url)
        self.assertNotIn('form', response.context)

    def test_authorized_client_has_form(self):
        """Проверяем, что автору передается форма."""
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], CommentForm)
