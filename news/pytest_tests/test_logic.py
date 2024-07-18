"""Тестирование логики через pytest."""

from pytest_django.asserts import assertRedirects, assertFormError
from django.conf import settings
from django.urls import reverse
from news.forms import WARNING, BAD_WORDS
from news.models import Comment
from http import HTTPStatus

COMMENT_TEXT = 'Бла-бла'
NEW_COMMENT_TEXT = 'Новое Бла-бла'


def test_anonymous_user_cant_create_comment(client, news, form_data):
    """Гость не может создать комментарий к новости."""
    client.post(settings.URL['detail'], data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
        author_client, form_data, news_id, news, author
):
    """Юзер может создать комментарий к новости."""
    url = reverse(settings.URL['detail'], args=news_id)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == NEW_COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news, news_id):
    """Юзер не может создать комментарий с запрещенными словами."""
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse(settings.URL['detail'], args=news_id)
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, comment_id, news_id):
    """Автор может удалить свой комментарий."""
    url = reverse(settings.URL['delete'], args=comment_id)
    news_url = reverse(settings.URL['detail'], args=news_id)
    url_to_comments = news_url + '#comments'
    response = author_client.delete(url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        not_author_client, comment_id
):
    """Юзер не может удалить чужой комментарий."""
    url = reverse(settings.URL['delete'], args=comment_id)
    response = not_author_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
        author_client, comment_id, news_id, form_data, comment
):
    """Автор может редактировать свой комментарий."""
    url = reverse(settings.URL['edit'], args=comment_id)
    response = author_client.post(url, data=form_data)
    news_url = reverse(settings.URL['detail'], args=news_id)
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(
        not_author_client, comment_id, form_data, comment
):
    """Юзер не может редактировать чужой комментарий."""
    url = reverse(settings.URL['edit'], args=comment_id)
    response = not_author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
