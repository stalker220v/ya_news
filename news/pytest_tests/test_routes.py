"""Тестирование доступности адресов через pytest."""

from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.mark.parametrize(
    'name, args',
    (
            ('news:home', None),
            ('news:detail', pytest.lazy_fixture('news_id')),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
    )
)
def test_pages_availability(client, name, args, news):
    """Данные адреса всем доступны."""
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
            (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
            (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name, args',
    (
            ('news:edit', pytest.lazy_fixture('comment_id')),
            ('news:delete', pytest.lazy_fixture('comment_id')),
    )
)
def test_availability_for_comment_edit_and_delete(
        expected_status, name, parametrized_client, args
):
    """Доступность редактирования и удаления комментариев автору и юзеру."""
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
            ('news:edit', pytest.lazy_fixture('comment_id')),
            ('news:delete', pytest.lazy_fixture('comment_id')),
    )
)
def test_redirect_for_anonymous_client(client, name, args):
    """Проверка редиректа гостя со страниц редактирования и удаления.
    Редирект на страницу входа.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
