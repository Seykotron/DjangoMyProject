from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.urls import reverse, resolve
from django.test import TestCase
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

class PasswordResetTests(TestCase):

    # Configuro el test
    def setUp(self):
        url = reverse("password_reset")
        self.response =  self.client.get( url )

    # Compruebo el status_code
    def test_status_code(self):
        self.assertEqual( self.response.status_code, 200 )

    # Compruebo que se ejecuta la vista correcta
    def test_view_function(self):
        view = resolve("/reset/")
        self.assertEqual( view.func.view_class, auth_views.PasswordResetView )

    # Compruebo el token CSRF
    def test_csrf(self):
        self.assertContains( self.response, "csrfmiddlewaretoken" )

    # Compruebo que el formulario mostrado es el deseado
    def test_contains_form(self):
        form = self.response.context.get("form")
        self.assertIsInstance( form, PasswordResetForm )

    # Compruebo los Inputs que la cantidad y el tipo esten bien
    def test_form_inputs(self):
        self.assertContains( self.response, "<input", 2 )
        self.assertContains( self.response, "type=\"email\"", 1 )

# Compruebo cuando se realiza un reseteo de password satisfactorio
class SuccessfulPasswordResetTest(TestCase):

    # Configuro el testcase
    def setUp(self):
        email = "john@doe.com"
        User.objects.create_user(username='john', email=email, password='123abcdef')
        url = reverse( "password_reset" )
        self.response = self.client.post( url, {"email" : email} )

    # Compruebo que la respuesta es una redirección
    def test_redirection(self):
        url = reverse( "password_reset_done" )
        self.assertRedirects( self.response, url )

    # Testeo que se haya enviado el email
    def test_send_password_reset_email(self):
        self.assertEqual(1, len(mail.outbox) )

# Compruebo cuando se realiza un reseteo inválido
class InvalidPasswordResetTests(TestCase):

    # Configuro el testcase
    def setUp(self):
        url = reverse("password_reset")
        self.response = self.client.post( url, {"email":"donotexists@email.com"} )

    # Compruebo que la respuesta es una redirección, aunque no sea un correo valido debería redireccionar
    def test_redirection(self):
        url = reverse( "password_reset_done" )
        self.assertRedirects( self.response, url )

    # Testeo que NO se haya enviado el email
    def test_no_reset_email_sent(self):
        self.assertEqual(0, len(mail.outbox) )

# Compruebo la pagina de reseteo de password hecho
class PasswordResetDoneTests(TestCase):

    # Configuro el testcase
    def setUp(self):
        url = reverse("password_reset_done")
        self.response = self.client.get( url )

    # Compruebo el status code
    def test_stats_code(self):
        self.assertEqual( self.response.status_code, 200 )

    # Compruebo que se cargue la vista indicada
    def test_view_function(self):
        view = resolve("/reset/done/")
        self.assertEqual( view.func.view_class, auth_views.PasswordResetDoneView )

# Compruebo que el reseteo de pasword funciona correctamente
class PasswordResetConfirmTests(TestCase):

    # Configuro el test para que genere un token válido
    def setUp(self):
        # Creo un usuario
        user = User.objects.create_user( username="john", email="john@doe.com", password="123abcdef" )

        # Creo el token tal y como lo haría al resetearse la password
        self.uid = urlsafe_base64_encode( force_bytes(user.pk) ).decode()
        self.token = default_token_generator.make_token( user )

        url = reverse( "password_reset_confirm", kwargs={ "uidb64" : self.uid, "token" : self.token } )
        self.response = self.client.get( url, follow=True )

    # Compruebo el status_code
    def test_status_code(self):
        self.assertEquals( self.response.status_code, 200 )

    # Compruebo que la vista que se muestra es la que se desea
    def test_view_function(self):
        view = resolve( "/reset/{uidb64}/{token}/".format( uidb64=self.uid, token=self.token ) )
        self.assertEqual( view.func.view_class, auth_views.PasswordResetConfirmView )

    # Compruebo que se muestra el token CSRF
    def test_csrf(self):
        self.assertContains( self.response, "csrfmiddlewaretoken" )

    # Compruebo que la respuesta contiene un formulario de la clase SetPasswordForm
    def test_contains_form(self):
        form = self.response.context.get("form")
        self.assertIsInstance( form, SetPasswordForm )

    # Compruebo los inputs del formulario, tiene 3, el CSRF y los 2 password field
    def test_form_inputs(self):
        self.assertContains( self.response, "<input", 3 )
        self.assertContains( self.response, 'type="password"', 2 )

# Compruebo que se comporta de la manera esperada cuando el token no es valido
class InvalidPasswordResetConfirmTests(TestCase):

    # Configuro el testcase
    def setUp(self):
        # Creo el usuario, el token y el uid
        user = User.objects.create_user( username="john", email="john@doe.com", password="123abcdef" )
        uid = urlsafe_base64_encode( force_bytes(user.pk) ).decode()
        token = default_token_generator.make_token( user )

        # Invalido el token cambiando la password del usuario
        user.set_password("abcdef123")
        user.save()

        url = reverse( "password_reset_confirm", kwargs={ "uidb64" : uid, "token" : token } )
        self.response = self.client.get( url )

    # Compruebo el status_code
    def test_status_code(self):
        self.assertEquals( self.response.status_code, 200 )

    # Compruebo el html devuelve que es inválido el link
    def test_html(self):
        password_reset_url = reverse("password_reset")
        self.assertContains( self.response, "enlace de reseteo de contraseña inválido" )
        self.assertContains( self.response, 'href="{0}"'.format(password_reset_url) )

# Compruebo que el mensaje de haber reseteado la password se muestra correctamente
class PasswordResetCompleteTests(TestCase):
    def setUp(self):
        url = reverse('password_reset_complete')
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/reset/complete/')
        self.assertEquals(view.func.view_class, auth_views.PasswordResetCompleteView)
