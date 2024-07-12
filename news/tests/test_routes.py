# news/tests/test_routes.py
# Импортируем класс HTTPStatus.
from http import HTTPStatus

# Импортируем функцию для определения модели пользователя.
from django.contrib.auth import get_user_model
from django.test import TestCase
# Импортируем функцию reverse().
from django.urls import reverse
# Импортируем класс модели новостей.
from news.models import Comment, News

# Получаем модель пользователя.
User = get_user_model()

class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(title='Заголовок', text='Текст')
        # создаём двух юзеров с разными именами
        cls.author = User.objects.create(username='Гегемон')
        cls.reader = User.objects.create(username='Гораций')
        # От имени одного пользователя создаём комментарий к новости:
        cls.comment = Comment.objects.create(
            news=cls.news,
            author=cls.author,
            text='Бла-бла'
        )

    def test_pages_availability(self):
        urls = (
            ('news:home', None),
            ('news:detail', (self.news.id,)),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_comment_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            # Логиним пользователя в клиенте:
            self.client.force_login(user)
            # Для каждой пары "пользователь - ожидаемый ответ"
            # перебираем имена тестируемых страниц:
            for name in ('news:edit', 'news:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.comment.id,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        # Сохраняем адрес страницы логина:
        login_url = reverse('users:login')
        # В цикле перебираем имена страниц, с которых ожидаем редирект:
        for name in ('news:edit', 'news:delete'):
            with self.subTest(name=name):
                # Получаем адрес страницы редактирования или удаления комментария:
                url = reverse(name, args=(self.comment.id,))
                # Получаем ожидаемый адрес страницы логина,
                # на который будет перенаправлен пользователь.
                # Учитываем, что в адресе будет параметр next, в котором передаётся
                # адрес страницы, с которой пользователь был переадресован.
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                # Проверяем, что редирект приведёт именно на указанную ссылку.
                self.assertRedirects(response, redirect_url)

    # объединили в test_pages_availability
    # def test_home_page(self):
    #     # Вызываем метод get для клиента (self.client)
    #     # и загружаем главную страницу.
    #     # Вместо прямого указания адреса
    #     # получаем его при помощи функции reverse().
    #     url = reverse('news:home')
    #     response = self.client.get(url)
    #     # Проверяем, что код ответа равен статусу OK (он же 200).
    #     self.assertEqual(response.status_code, HTTPStatus.OK)

    # объединили в test_pages_availability
    # def test_detail_page(self):
    #     # Правильным решением будет обратиться к адресу страницы через функцию reverse(). В неё надо передать
    #     # namespace и name страницы — увидеть их можно в файле urls.py приложения; в нашем случае это 'news:detail'
    #     # pk (Primary Key) записи; в нашем случае pk совпадает с id.
    #     # Передать необходимые значения в функцию reverse() можно через позиционные или именованные аргументы:
    #     # url = reverse('news:detail', args=(self.news.pk,))
    #     # # Или
    #     # url = reverse('news:detail', kwargs={'pk': self.news.pk})
    #     # В каждом из приведённых вариантов происходит одно и то же — переменной url присваивается строка '/news/1/'.
    #     # То же самое можно сделать, указывая id объекта, а не pk. При этом нужно помнить, что вообще-то
    #     # первичный ключ не всегда равен id, и в каких-то проектах он может быть другим.
    #     url = reverse('news:detail', args=(self.news.id,))
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, HTTPStatus.OK)
