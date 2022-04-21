from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from posts.tests.test_urls import PostURLTests

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testusername')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Описание группы',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}
                    ): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'testusername'}
                    ): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': PostPagesTests.post.id}
                    ): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': PostPagesTests.post.id}
                    ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }

        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_and_group_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        templates_context = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.user.username})
        }
        for template_context in templates_context:
            with self.subTest(template_context=template_context):
                response = self.authorized_client.get(template_context)
                first_post = response.context['page_obj'][0]
                self.assertEqual(
                    first_post.text,
                    PostURLTests.post.text)
                self.assertEqual(
                    first_post.author.username,
                    PostURLTests.post.author.username)
                self.assertEqual(
                    first_post.group.title,
                    PostURLTests.post.group.title)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={
                'username': f'{self.user.username}'}))
        first_post = response.context['page_obj'][0]
        self.assertEqual(
            first_post.text,
            PostURLTests.post.text)
        self.assertEqual(
            first_post.author.username,
            PostURLTests.post.author.username)
        self.assertEqual(
            first_post.group.title,
            PostURLTests.post.group.title)
