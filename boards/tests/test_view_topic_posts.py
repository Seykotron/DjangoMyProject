from django.urls import reverse, resolve
from django.test import TestCase
from boards.views import Home, TopicListView, NewTopic, TopicPosts
from django.contrib.auth.models import User

from ..models import Board, Topic, Post
from ..forms import NewTopicForm

class TopicPostsTests(TestCase):
    # Configuro el testcsae
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        self.user = User.objects.create_user(username='john', email='john@doe.com', password='123')
        self.topic = Topic.objects.create(subject='Hello, world', board=self.board, starter=self.user)
        Post.objects.create(message='Lorem ipsum dolor sit amet', topic=self.topic, created_by=self.user)
        url = reverse('topic_posts', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})
        self.response = self.client.get(url)

    # Compruebo el status_code
    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    # Compruebo que la vista devuelta sea la esperada
    def test_view_function(self):
        view = resolve('/boards/{0}/topics/{1}/'.format( self.board.pk, self.topic.pk ) )
        self.assertEquals(view.func.view_class, TopicPosts)
