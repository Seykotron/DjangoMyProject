from django.urls import reverse, resolve
from django.test import TestCase
from boards.views import Home, TopicListView, NewTopic
from ..models import Board, Topic, Post
from django.contrib.auth.models import User
from ..forms import NewTopicForm

# Test para la Home
class HomeTests(TestCase):

    def setUp(self):
        self.board = Board.objects.create( name="Django", description="Django board." )
        url = reverse("home")
        self.response = self.client.get(url)

    # Compruebo que devuelve un status_code bueno
    def test_home_view_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    # Compruebo que la peticion / devuelve un objeto de tipo home
    def test_home_url_resolves_home_view(self):
        view = resolve("/")
        # De esta manera se comprueba que la vista que se esta visionando coincide con la que
        # devuelve el ejecutar el metodo Home.as_view()
        self.assertEqual(view.func.view_class, Home)

    def test_home_view_contains_link_to_topics_page(self):
        # Cargamos las topic url
        board_topics_url = reverse( "board_topics", kwargs={"pk": self.board.pk} )
        self.assertContains(self.response, "href=\"{0}\"".format(board_topics_url) )
