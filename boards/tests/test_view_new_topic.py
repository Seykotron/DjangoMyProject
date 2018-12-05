from django.urls import reverse, resolve
from django.test import TestCase
from boards.views import Home, TopicListView, NewTopic
from ..models import Board, Topic, Post
from django.contrib.auth.models import User
from ..forms import NewTopicForm

# Comprobación de que funciona el login_required
class LoginRequiredNewTopicTests(TestCase):
    # Configuro el testcase
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        self.url = reverse('new_topic', kwargs={ 'pk': self.board.pk })
        self.response = self.client.get(self.url)

    # Compruebo que se realiza una redirección
    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

# Creo los test para la vista de agregar Topics
class NewTopicTest(TestCase):

    # Hago las acciones necesarias para empezar el test
    # def setUp(self):
    #     Board.objects.create(name="Django", description="Django board.")

    # Agrego un Board para las pruebas
    def setUp(self):
        self.board   = Board.objects.create(name='Django', description='Django board.')
        self.user    = User.objects.create_user(username='john', email='john@doe.com', password='123')
        self.client.login(username='john', password='123')

    # Compruebo el status_code 200
    def test_new_topic_view_success_status_code(self):
        url = reverse('new_topic', kwargs={'pk': self.board.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    # Compruebo que para un objeto inexistente devuelve un 404
    def test_new_topic_view_not_found_status_code(self):
        url = reverse( "new_topic", kwargs={"pk" : self.board.pk+1})
        response = self.client.get( url )
        self.assertEqual( response.status_code, 404 )

    # Compruebo que resuelve bien la vista de nuevo topic
    def test_new_topic_url_resolves_new_topic_view(self):
        view = resolve("/boards/{0}/new/".format(self.board.pk))
        self.assertEqual( view.func.view_class, NewTopic )

    # Compruebo que existen links de vuelta a la lista de los Topics
    def test_new_topic_view_contains_links_back_to_board_topics_views(self):
        new_topic_url = reverse( "new_topic", kwargs={"pk" : self.board.pk } )
        board_topics_url = reverse( "board_topics", kwargs={ "pk" : self.board.pk } )
        response = self.client.get( new_topic_url )
        self.assertContains( response, 'href="{0}"'.format(board_topics_url) )

    # Compruebo que está el token CSRF
    def test_csrf(self):
        url = reverse( "new_topic", kwargs={"pk": self.board.pk} )
        response = self.client.get( url )
        self.assertContains( response, "csrfmiddlewaretoken" )

    # Compruebo que ocurre si se postea datos validos
    def test_new_topic_valid_post_data(self):
        url = reverse( "new_topic", kwargs={"pk": self.board.pk} )
        data = {
            "subject" : "Test title",
            "message" : "Lorem ipsum lorum sit amet"
        }
        response = self.client.post( url, data )
        self.assertTrue( Topic.objects.exists() )
        self.assertTrue( Post.objects.exists() )

    # Compruebo que ocurre si envio datos invalidos
    # Compruebo que aparecen errores de validacion
    def test_new_topic_invalid_post_data(self):
        """
            Al enviar datos inválidos se espera que el form devuelva un 200 y no redirija,
            y esta vez incluya errores de validación
        """
        url = reverse( "new_topic", kwargs={"pk": self.board.pk})
        response = self.client.post( url, {})
        form = response.context.get('form')
        self.assertEqual( response.status_code, 200 )
        self.assertTrue( form.errors )

    # Compruebo qué ocurre si envio datos en vacío
    # Compruebo que aparecen errores de validacion
    def test_new_topic_invalid_post_data_empty_fields(self):
        """
            Al enviar datos inválidos (esta vez vacios) se espera un 200 y no redirigir y
            que se incluyan errores de validación
        """
        url = reverse( "new_topic", kwargs={"pk": self.board.pk})
        data = {
            "subject" : "",
            "message" : ""
        }
        response = self.client.post( url, data)
        form = response.context.get('form')
        self.assertEqual( response.status_code, 200 )
        self.assertFalse( Topic.objects.exists() )
        self.assertFalse( Post.objects.exists() )
        self.assertTrue( form.errors )

    # Compruebo que la página contiene un formulario
    def test_contains_form(self):
        url = reverse( "new_topic", kwargs={"pk":self.board.pk})
        response = self.client.get( url )
        form = response.context.get("form")
        self.assertIsInstance( form, NewTopicForm )
