from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from ..forms import SignUpForm
from ..views import Signup

# Compruebo la vista del registro si esta bien o no
class SignUpTests(TestCase):

    # Configuramos la prueba desde el setUp
    def setUp(self):
        url = reverse("signup")
        self.response = self.client.get( url )

    # Compruebo que devuelva status_code de 200
    def test_signup_status_code(self):
        self.assertEqual( self.response.status_code, 200 )

    # Compruebo que devuelve la vista que tiene que ser
    def test_signup_url_resolves_signup_view(self):
        view = resolve("/signup/")
        self.assertEqual( view.func.view_class, Signup )

    # Compruebo que existe csrf
    def test_csrf(self):
        self.assertContains( self.response, "csrfmiddlewaretoken" )

    # Compruebo que contenga un formulario
    def test_contains_form(self):
        form = self.response.context.get("form")
        self.assertIsInstance( form, SignUpForm )

    # Compruebo los campos del formulario
    def test_form_inputs(self):
        self.assertContains( self.response, "<input", 5 )
        self.assertContains( self.response, "type=\"text\"",1 )
        self.assertContains( self.response, "type=\"email\"",1 )
        self.assertContains( self.response, "type=\"password\"", 2)

# Compruebo que se realizan bien los registros
class SuccessfulSignUpTest(TestCase):

    # Configuro el test
    def setUp(self):
        self.home_url = reverse("home")
        url = reverse( "signup" )
        data = {
            'username': 'john',
            'password1': 'abcdef123456',
            'password2': 'abcdef123456',
            "email" : "john@doe.com"
        }
        self.response = self.client.post( url, data )

    # Compruebo la redirección
    def test_redirection(self):
        self.assertRedirects( self.response, self.home_url )

    # Compruebo que el usuario se ha creado
    def test_user_creation(self):
        self.assertTrue( User.objects.exists() )

    # Compruebo que el usuario está autenticado
    def test_user_authentication(self):
        response = self.client.get( self.home_url )
        user = response.context.get("user")
        self.assertTrue( user.is_authenticated )


# Compruebo que no se realizan registros con formularios mal formados
class InvalidSignUpTests(TestCase):

    # Configuro el test
    def setUp(self):
        url = reverse("signup")
        self.response = self.client.post( url, {} )

    # Compruebo que el status_code sea 200 por lo tanto no ha habido redirección
    def test_signup_status_code(self):
        self.assertEqual( self.response.status_code, 200 )

    # Compruebo que exiten errores en el formulario
    def test_form_errors(self):
        form = self.response.context.get("form")
        self.assertTrue( form.errors )

    # Compruebo que no se ha creado ningun usuario
    def test_dont_create_user(self):
        self.assertFalse( User.objects.exists() )
