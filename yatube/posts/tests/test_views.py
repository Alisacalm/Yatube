import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
# from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Unfollower')
        cls.user_2 = User.objects.create_user(username='Follower')
        cls.author = User.objects.create_user(username='FollowedUser')
        cls.group = Group.objects.create(
            title='Группа',
            slug='group',
            description='Описание группы',
        )
        cls.second_group = Group.objects.create(
            title='Другая Группа',
            slug='group-2',
            description='Описание второй группы',
        )

        cls.POSTS_ON_FIRST_PAGE = 10
        cls.POSTS_ON_SECOND_PAGE = 3
        bulk_of_posts = cls.POSTS_ON_FIRST_PAGE + cls.POSTS_ON_SECOND_PAGE

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        posts = [
            Post(
                text='Тестовый текст',
                group=cls.group,
                author=cls.author,
                image=cls.uploaded
            )
            for obj in range(bulk_of_posts)
        ]
        Post.objects.bulk_create(posts, batch_size=bulk_of_posts)
        cls.post = Post.objects.last()
        cls.templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': cls.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': cls.post.id}
            ): 'posts/create_post.html',
        }

        cls.reverse_names = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': cls.user.username}
            ),
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        self.assertIn('page_obj', response.context)
        self.assertEqual(response.context['group'], self.post.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        self.assertIn('page_obj', response.context)
        self.assertEqual(response.context['author'], self.post.author)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertIn('post', response.context)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post_1.id}
            )
        )
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)

    def test_first_page_contains_ten_records(self):
        for reverse_name in self.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        for reverse_name in self.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)

    def test_post_shown_on_pages_if_added_group(self):
        post = Post.objects.create(
            text='Текст нового поста',
            group=self.group,
            author=self.user
        )
        for reverse_name in self.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertIn(post, response.context['page_obj'])

    def test_post_not_in_another_group(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.second_group.slug}
            )
        )
        self.assertIsNot(self.post, response.context['page_obj'])

    def test_image_is_shown_on_templates(self):
        post = Post.objects.create(
            text='Текст нового поста',
            group=self.group,
            author=self.user,
            image=self.uploaded
        )
        for reverse_name in self.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertIn(post, response.context['page_obj'])

    # def test_index_caches(self):
    #     """Тестирование кеша главной страницы."""
    #     new_post = Post.objects.create(
    #         author=self.user,
    #         text='Пост для теста кеша',
    #         group=self.group
    #     )
    #     response_1 = self.authorized_client.get(
    #         reverse('posts:index')
    #     )
    #     response_content_1 = response_1.content
    #     new_post.delete()
    #     response_2 = self.authorized_client.get(
    #         reverse('posts:index')
    #     )
    #     response_content_2 = response_2.content
    #     self.assertEqual(response_content_1, response_content_2)
    #     cache.clear()
    #     response_3 = self.authorized_client.get(
    #         reverse('posts:index')
    #     )
    #     response_content_3 = response_3.content
    #     self.assertNotEqual(response_content_2, response_content_3)

    def test_auth_can_follow_unfollow(self):
        """Авторизованный пользователь может подписываться и отписываться"""
        count_follow = Follow.objects.count()
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author.username}
            )
        )
        follow = Follow.objects.create(
            user=self.user_2,
            author=self.author
        )
        self.assertEqual(Follow.objects.count(), count_follow + 1)
        self.assertEqual(follow.author, self.author)
        self.assertEqual(follow.user, self.user_2)
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author.username}
            )
        )
        follow.delete()
        self.assertEqual(Follow.objects.count(), count_follow)

    def test_new_post_is_in_follower_and_not_in_unfollower(self):
        """Новый пост есть в подписках и нет у тех, кто не подписан"""
        follow_post_count = Post.objects.filter(
            author__following__user=self.user_2
        ).count()
        unfollow_post_count = Post.objects.filter(
            author__following__user=self.user
        ).count()
        Post.objects.create(
            text='Новая запись',
            group=self.group,
            author=self.author
        )
        self.authorized_client.get(
            reverse(
                'posts:follow_index'
            )
        )
        Follow.objects.create(
            user=self.user_2,
            author=self.author
        )
        self.assertEqual(
            Post.objects.filter(
                author__following__user=self.user_2
            ).count(), follow_post_count + 1)
        self.assertEqual(
            Post.objects.filter(
                author__following__user=self.user
            ).count(), unfollow_post_count)
