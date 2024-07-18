"""Фикстуры для pytest."""

import pytest
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.test.client import Client

from news.models import Comment, News


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    """Модель автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Модель пользователя."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Логиним автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Логиним другого пользователя."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture(autouse=True)
def news(author):
    """Создаём новость."""
    news = News.objects.create(title='Заголовок', text='Текст')
    return news


@pytest.fixture
def comment(author, news):
    """Создаём комментарий."""
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Бла-бла'
    )
    return comment


@pytest.fixture
def news_id(news):
    """Получаем id новости."""
    return (news.id,)


@pytest.fixture
def comment_id(comment):
    """Получаем id комментария."""
    return (comment.id,)


@pytest.fixture
def news10_in_one_page(author):
    """Создаём сразу 10 новостей."""
    today = timezone.now()
    all_news = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(
            title=f'Новость {index}',
            text='Просто текст.',
            # Для каждой новости уменьшаем дату на index дней от today,
            # где index - счётчик цикла.
            date=today - timedelta(days=index)
        )
        all_news.append(news)
    news_10 = News.objects.bulk_create(all_news)
    return news_10


@pytest.fixture
def comment10_in_one_page_news(author, news):
    """Создаём сразу 10 комментариев."""
    now = timezone.now()
    all_comment = []
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        all_comment.append(comment)
    return all_comment


@pytest.fixture
def form_data():
    """Данные для создания."""
    return {
        'text': 'Новое Бла-бла',
    }
