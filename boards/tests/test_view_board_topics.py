from django.urls import reverse, resolve
from django.test import TestCase
from boards.views import Home, TopicListView, NewTopic, TopicListView
from ..models import Board, Topic, Post
from django.contrib.auth.models import User
from ..forms import NewTopicForm


# Creo los test para la lista de Topics en los Board
class BoardTopicsTests(TestCase):
    # Hago las acciones necesarias para empezar el test
    # def setUp(self):
    #     self.board = Board(name="Django", description="Django board.")
    #     self.board.save()

    @classmethod
    def setUpTestData(cls):
        cls.board = Board.objects.create(name="Django", description="Django board.")

    # Compruebo el status_code 200
    def test_board_topics_view_status_code(self):
        url = reverse("board_topics", kwargs={"pk":self.board.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    # Compruebo el status_code 404
    def test_board_topics_view_not_found_status_code(self):
        url = reverse("board_topics", kwargs={"pk" : self.board.pk+1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    # Compruebo que resuelve bien el board
    def test_board_topics_url_resolves_board_topics_views(self):
        view = resolve("/boards/{0}/".format( self.board.pk ))
        self.assertEqual( view.func.view_class, TopicListView )

    # Compruebo que el Board tiene un link de vuelta a la homepage
    def test_board_topics_view_contains_link_back_to_homepage(self):
        board_topics_url = reverse("board_topics", kwargs={"pk":self.board.pk})
        response = self.client.get(board_topics_url)
        homepage_url = reverse("home")
        self.assertContains( response, 'href="{0}"'.format(homepage_url) )

    # Compruebo que la vista tiene los links de navegación correctos
    def test_board_topics_view_contains_navigation_links(self):
        board_topics_url = reverse( "board_topics", kwargs={"pk": self.board.pk} )
        homepage_url = reverse("home")
        new_topic_url = reverse("new_topic", kwargs={"pk": self.board.pk})

        response = self.client.get( board_topics_url )

        self.assertContains( response, 'href="{0}"'.format(homepage_url) )
        self.assertContains( response, 'href="{0}"'.format(new_topic_url) )
