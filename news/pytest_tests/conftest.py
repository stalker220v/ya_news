# conftest.py
import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
# Импортируем класс клиента.
from django.test.client import Client

# Импортируем модель заметки, чтобы создать экземпляр.
from news.models import Comment, News

@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')

@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')

@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client

@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client

@pytest.fixture(autouse=True)
def news(author):
    news = News.objects.create(title='Заголовок', text='Текст')
    return news

@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Бла-бла'
    )
    return comment

@pytest.fixture
def news_id(news):
    return (news.id,)

@pytest.fixture
def comment_id(comment):
    return (comment.id,)

@pytest.fixture
def news10_in_one_page(author):
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
    now = timezone.now()
    all_comment = []
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        # Сразу после создания меняем время создания комментария.
        comment.created = now + timedelta(days=index)
        # И сохраняем эти изменения.
        comment.save()
        all_comment.append(comment)
    return all_comment


