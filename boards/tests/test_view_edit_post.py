from django.forms import ModelForm

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from ..models import Board, Post, Topic
from ..views import PostUpdateView


# Configuro la base de la que parten todos los tests
class PostUpdateViewTestCase(TestCase):

    # Configuro la clase
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        self.username = 'john'
        self.password = '123'
        user = User.objects.create_user(username=self.username, email='john@doe.com', password=self.password)
        self.topic = Topic.objects.create(subject='Hello, world', board=self.board, starter=user)
        self.post = Post.objects.create(message='Lorem ipsum dolor sit amet', topic=self.topic, created_by=user)
        self.url = reverse('edit_post', kwargs={
            'pk': self.board.pk,
            'topic_pk': self.topic.pk,
            'post_pk': self.post.pk
        })

# Compruebo que haga falta estar logueado
class LoginRequiredPostUpdateViewTests(PostUpdateViewTestCase):
    def test_redirection(self):
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

# Compruebo que no se pueda actualizra un post que no sea propio
class UnauthorizedPostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        super().setUp()
        # Creo otro usuario
        username = 'jane'
        password = '321'
        user = User.objects.create_user(username=username, email='jane@doe.com', password=password)
        # Logueo al usuario
        self.client.login(username=username, password=password)
        # Realizo la petición para ver la página de update
        self.response = self.client.get(self.url)

    # Un post solo puede ser editado por su dueño, si no eres el dueño devuelve un 404
    def test_status_code(self):
        self.assertEquals(self.response.status_code, 404)

# Compruebo que las vistas crecen al visitar
class PostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.get(self.url)

    # Compruebo que el status_code sea 200
    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    # Compruebo que la vista que se devuelve es la correcta
    def test_view_class(self):
        view = resolve( '/boards/{0}/topics/{1}/posts/{2}/edit/'.format(self.board.pk,self.topic.pk,self.post.pk) )
        self.assertEquals(view.func.view_class, PostUpdateView)

    # Compruebo que dispone de token CSRF
    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    # Compruebo que el formulario es el que debe ser
    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, ModelForm)

    # Compruebo que los input son los que son y ninguno más
    def test_form_inputs(self):
        self.assertContains(self.response, '<input', 1)
        self.assertContains(self.response, '<textarea', 1)

# Compruebo que el post se ha actualizado correctamente
class SuccessfulPostUpdateViewTests(PostUpdateViewTestCase):
    # Hago login válido y actualizo el post
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {'message': 'edited message'})

    # Una actualización válida te lleva a la página de posts
    def test_redirection(self):
        topic_posts_url = reverse('topic_posts', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})
        self.assertRedirects(self.response, topic_posts_url)

    # Compruebo que el post ha cambiado
    def test_post_changed(self):
        self.post.refresh_from_db()
        self.assertEquals(self.post.message, 'edited message')

# Compruebo que no se realizan cambios al post cuando no se debe
class InvalidPostUpdateViewTests(PostUpdateViewTestCase):
    # Enviamos un diccionario vacío con un usuario autenticado correctamente
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {})

    # Comprobamos que no redirije y nos devuelve un 200 al ser inválido
    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    # Comprobmaos que el post tiene errores
    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)
