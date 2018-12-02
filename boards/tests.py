from django.urls import reverse, resolve
from django.test import TestCase
from boards.views import Home

# Create your tests here.

# Test para la Home
class HomeTests(TestCase):
    # Compruebo que devuelve un status_code bueno
    def test_home_view_status_code(self):
        url = reverse("home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    # Compruebo que la peticion / devuelve un objeto de tipo home
    def test_home_url_resolves_home_view(self):
        view = resolve("/")
        # De esta manera se comprueba que la vista que se esta visionando coincide con la que
        # devuelve el ejecutar el metodo Home.as_view()
        self.assertEqual(view.func.__name__, Home.as_view().__name__)
