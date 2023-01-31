from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from . .models import Group, Post, User

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Группа',
            slug='group',
            description='Описание группы'
        )
        cls.post = Post.objects.create(
            text='Текст поста',
            group=cls.group,
            author=cls.user
        )

        cls.public_urls = [
            '/', f'/group/{cls.group.slug}/',
            f'/profile/{cls.user.username}/',
            f'/posts/{cls.post.id}/'
        ]

        cls.auth_urls = {
            '/create/': HTTPStatus.OK,
            f'/posts/{cls.post.id}/comment/': HTTPStatus.FOUND,
        }

        cls.url_template = {
            '/': 'posts/index.html',
            '/group/group/': 'posts/group_list.html',
            '/profile/user/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{cls.post.id}/edit/': 'posts/create_post.html'
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_for_guest_client(self):
        for url in self.public_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_for_authorized_client_user(self):
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_for_authorized_client(self):
        for url, status_code in self.auth_urls.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_url_unexisting_page(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_to_authorize(self):
        url_list_auth = [
            f'/posts/{self.post.id}/edit/',
            '/create/'
        ]
        for url in url_list_auth:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response, (f'/auth/login/?next={url}')
                )

    def test_template_to_url(self):
        for url, template in self.url_template.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
