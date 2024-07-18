"""Тестирование контента через pytest."""

from django.conf import settings
from django.urls import reverse
from news.forms import CommentForm


def test_news_count(client, news10_in_one_page):
    """Проверяем, что на домашней странице 10 новостей."""
    url = reverse(settings.URL['home'])
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news10_in_one_page):
    """Проверяем сортировку новостей по времени убывания."""
    url = reverse(settings.URL['home'])
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(
        client, author, news, comment10_in_one_page_news, news_id
):
    """Проверяем сортировку комментариев по времени убывания."""
    url = reverse(settings.URL['detail'], args=news_id)
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, news, news_id):
    """Проверяем, что гостю не передается форма."""
    url = reverse(settings.URL['detail'], args=news_id)
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author, client, news, news_id):
    """Проверяем, что автору передается форма."""
    client.force_login(author)
    url = reverse(settings.URL['detail'], args=news_id)
    response = client.get(url)
    assert 'form' in response.context
    assert type(response.context['form']) == CommentForm
