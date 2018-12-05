from django.urls import reverse, resolve
from django.test import TestCase
from boards.views import Home, TopicListView, NewTopic, TopicPosts, ReplyTopic
from django.contrib.auth.models import User

from ..models import Board, Topic, Post
from ..forms import NewTopicForm, PostForm

class ReplyTopicTestCase(TestCase):

    # Configuramos la base que se va a usar en todos los test de respuesta
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        self.username = 'john'
        self.password = '123'
        user = User.objects.create_user(username=self.username, email='john@doe.com', password=self.password)
        self.topic = Topic.objects.create(subject='Hello, world', board=self.board, starter=user)
        Post.objects.create(message='Lorem ipsum dolor sit amet', topic=self.topic, created_by=user)
        self.url = reverse('reply_topic', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})

# Comprobamos que haga falta estar logueado para funcionar
class LoginRequiredReplyTopicTests(ReplyTopicTestCase):
    # Comprobamos la redirección
    def test_redirection(self):
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

# Comprobamos que se pueden contestar a los topic
class ReplyTopicTests(ReplyTopicTestCase):

    # Configuramos el testcase llamando al padre
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.get(self.url)

    # Se comprueba el status_code
    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    # Se comprueba que la vista devuelta es la esperada
    def test_view_function(self):
        view = resolve('/boards/{0}/topics/{1}/reply/'.format( self.board.pk, self.topic.pk ))
        self.assertEquals(view.func.view_class, ReplyTopic)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    # Compruebo que el formulario es de la clase que queremos que sea
    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, PostForm)

    # Compruebo que el formulario creado tiene los campos necesarios
    def test_form_inputs(self):
        self.assertContains(self.response, '<input', 1)
        self.assertContains(self.response, '<textarea', 1)

# Comprobamos un posteo válido
class SuccessfulReplyTopicTests(ReplyTopicTestCase):
    # Configuramos el testcase con un usuario logueado y un mensaje relleno
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {'message': 'hello, world!'})

    # Se comprueba si se hace la redirección
    def test_redirection(self):
        url = reverse('topic_posts', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})
        topic_posts_url = '{url}?page=1#2'.format(url=url)
        self.assertRedirects(self.response, topic_posts_url)

    # Se comprueba la cantidad de Posts que hay (que deben de ser 2, el creado inicialmente y la contestación)
    def test_reply_created(self):
        self.assertEquals(Post.objects.count(), 2)

# Comprobamos un posteo invalido
class InvalidReplyTopicTests(ReplyTopicTestCase):
    # Configuramos el testcase enviando los campos del post vacíos
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {})

    # Un envío inválido debería devolver un 200 y devolverte a la misma página
    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    # Compruebo que el formulario contiene errores
    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)
