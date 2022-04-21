from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from http.client import OK

from posts.forms import PostForm
from posts.models import Post, Group
from posts.models import User

User = get_user_model()


class PostFormsTests(TestCase):
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
            text='Тестовый пост',
            author=cls.user
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(PostFormsTests.user)

    def test_create_post(self):
        '''Тест создания поста.'''
        posts_count = Post.objects.count()
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group.id}
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)
        error_name1 = 'Данные поста не совпадают'
        self.assertEqual(response.status_code, OK)
        self.assertTrue(Post.objects.filter(
                        text='Текст записанный в форму',
                        group=1,
                        author=self.user
                        ).exists(), error_name1)
        error_name2 = 'Поcт не добавлен в БД'
        self.assertEqual(Post.objects.count(),
                         posts_count + 1,
                         error_name2)

    def test_edit_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост'
        }
        response = self.author_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk}),
            data=form_data, follow=True)
        self.assertEqual(
            Post.objects.count(), posts_count, 'Количество постов увеличилось')
        num_post = response.context['post']
        text = num_post.text
        self.assertEqual(text, self.post.text)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}
        ))
