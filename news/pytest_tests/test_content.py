"""Тестирование контента через pytest."""

from django.conf import settings
from django.urls import reverse
from news.forms import CommentForm


def test_news_count(client, news10_in_one_page):
    """Проверяем, что на домашней странице 10 новостей."""
    url = reverse(settings.URL['home'])
    response = client.get(url)
    # Код ответа не проверяем, его уже проверили в тестах маршрутов.
    # Получаем список объектов из словаря контекста.
    object_list = response.context['object_list']
    # Определяем количество записей в списке.
    news_count = object_list.count()
    # Проверяем, что на странице именно 10 новостей.
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news10_in_one_page):
    """Проверяем сортировку новостей по времени убывания."""
    url = reverse(settings.URL['home'])
    response = client.get(url)
    # Получаем список объектов из словаря контекста.
    object_list = response.context['object_list']
    # Получаем даты новостей в том порядке, как они выведены на странице.
    all_dates = [news.date for news in object_list]
    # Сортируем полученный список по убыванию.
    sorted_dates = sorted(all_dates, reverse=True)
    # Проверяем, что исходный список был отсортирован правильно.
    assert all_dates == sorted_dates


def test_comments_order(
        client, author, news, comment10_in_one_page_news, news_id
):
    """Проверяем сортировку комментариев по времени убывания."""
    url = reverse(settings.URL['detail'], args=news_id)
    response = client.get(url)
    # Проверяем, что объект новости находится в словаре контекста
    # под ожидаемым именем - названием модели.
    assert 'news' in response.context
    # Получаем объект новости.
    news = response.context['news']
    # Получаем все комментарии к новости.
    all_comments = news.comment_set.all()
    # Собираем временные метки всех новостей.
    all_timestamps = [comment.created for comment in all_comments]
    # Сортируем временные метки, менять порядок сортировки не надо.
    sorted_timestamps = sorted(all_timestamps)
    # Проверяем, что временные метки отсортированы правильно.
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, news, news_id):

    # первый тест проверит, что при запросе анонимного пользователя форма не передаётся
    # в словаре контекста.
    url = reverse(settings.URL['detail'], args=news_id)
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author, client, news, news_id):
    # Авторизуем клиент при помощи ранее созданного пользователя.
    client.force_login(author)
    url = reverse(settings.URL['detail'], args=news_id)
    response = client.get(url)
    assert 'form' in response.context
    # а так же проверим, что объект формы соответствует нужному классу формы.
    assert type(response.context['form']) == CommentForm
