"""Тестирование логики через pytest."""
# test_logic.py
# Импортируем функции для проверки редиректа и ошибки формы:
from pytest_django.asserts import assertRedirects, assertFormError
import pytest
from django.conf import settings
from django.urls import reverse
# Импортируем из модуля forms сообщение об ошибке:
from news.forms import WARNING, BAD_WORDS
from news.models import Comment, News
# Дополнительно импортируем функцию slugify.
from pytils.translit import slugify
# Допишите импорт класса со статусами HTTP-ответов.
from http import HTTPStatus

COMMENT_TEXT = 'Бла-бла'
NEW_COMMENT_TEXT = 'Новое Бла-бла'

def test_anonymous_user_cant_create_comment(client, news, form_data):
    # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
    # предварительно подготовленные данные формы с текстом комментария.
    client.post(settings.URL['detail'], data=form_data)
    # Считаем количество комментариев.
    comments_count = Comment.objects.count()
    # Ожидаем, что комментариев в базе нет - сравниваем с нулём.
    assert comments_count == 0

def test_user_can_create_comment(author_client, form_data, news_id, news, author):
    # Совершаем запрос через авторизованный клиент.
    url = reverse(settings.URL['detail'], args=news_id)
    response = author_client.post(url, data=form_data)
    # Проверяем, что редирект привёл к разделу с комментами.
    assertRedirects(response, f'{url}#comments')
    # Считаем количество комментариев.
    comments_count = Comment.objects.count()
    # Убеждаемся, что есть один комментарий.
    assert comments_count == 1
    # Получаем объект комментария из базы.
    comment = Comment.objects.get()
    # Проверяем, что все атрибуты комментария совпадают с ожидаемыми.
    assert comment.text == NEW_COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author

def test_user_cant_use_bad_words(author_client, news, news_id):
    # Формируем данные для отправки формы; текст включает
    # первое слово из списка стоп-слов.
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    # Отправляем запрос через авторизованный клиент.
    url = reverse(settings.URL['detail'], args=news_id)
    response = author_client.post(url, data=bad_words_data)
    # Проверяем, есть ли в ответе ошибка формы.
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    # Дополнительно убедимся, что комментарий не был создан.
    comments_count = Comment.objects.count()
    assert comments_count == 0

def test_author_can_delete_comment(author_client, comment_id, news_id):
    # От имени автора комментария отправляем DELETE-запрос на удаление.
    url = reverse(settings.URL['delete'], args=comment_id)
    news_url = reverse(settings.URL['detail'], args=news_id)  # Адрес новости.
    url_to_comments = news_url + '#comments'  # Адрес блока с комментариями.
    response = author_client.delete(url)
    # Проверяем, что редирект привёл к разделу с комментариями.
    # Заодно проверим статус-коды ответов.
    assertRedirects(response, url_to_comments)
    # Считаем количество комментариев в системе.
    comments_count = Comment.objects.count()
    # Ожидаем ноль комментариев в системе.
    assert comments_count == 0

def test_user_cant_delete_comment_of_another_user(not_author_client, comment_id):
    # Выполняем запрос на удаление от пользователя-читателя.
    url = reverse(settings.URL['delete'], args=comment_id)
    response = not_author_client.delete(url)
    # Проверяем, что вернулась 404 ошибка.
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Убедимся, что комментарий по-прежнему на месте.
    comments_count = Comment.objects.count()
    assert comments_count == 1

def test_author_can_edit_comment(author_client, comment_id, news_id, form_data, comment):
    # Выполняем запрос на редактирование от имени автора комментария.
    url = reverse(settings.URL['edit'], args=comment_id)
    response = author_client.post(url, data=form_data)
    news_url = reverse(settings.URL['detail'], args=news_id)  # Адрес новости.
    url_to_comments = news_url + '#comments'  # Адрес блока с комментариями.
    # Проверяем, что сработал редирект.
    assertRedirects(response, url_to_comments)
    # Обновляем объект комментария.
    comment.refresh_from_db()
    # Проверяем, что текст комментария соответствует обновленному.
    assert comment.text == NEW_COMMENT_TEXT

def test_user_cant_edit_comment_of_another_user(not_author_client, comment_id, form_data, comment):
    # Выполняем запрос на редактирование от имени другого пользователя.
    url = reverse(settings.URL['edit'], args=comment_id)
    response = not_author_client.post(url, data=form_data)
    # Проверяем, что вернулась 404 ошибка.
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Обновляем объект комментария.
    comment.refresh_from_db()
    # Проверяем, что текст остался тем же, что и был.
    assert comment.text == COMMENT_TEXT
