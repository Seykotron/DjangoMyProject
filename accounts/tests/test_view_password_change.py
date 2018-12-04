from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views
from django.urls import resolve, reverse
from django.test import TestCase

# Compruebo el proceso de cambio de password de un usuario
class PasswordChangeTests(TestCase):

    # Configuro el testcase, creo un usuario y me logueo como el
    def setUp(self):
        username="john"
        password="secret123"
        user = User.objects.create_user( username=username, email="john@doe.com", password=password )
        url = reverse('password_change')
        self.client.login( username=username, password=password )
        self.response = self.client.get(url)

    # Compruebo el status_code
    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    # Compruebo que la vista mostrada es la esperada
    def test_url_resolve_correct_view(self):
        view = resolve('/settings/password/')
        self.assertEquals(view.func.view_class, auth_views.PasswordChangeView)

    # Compruebo el token CSRF
    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    # Compruebo que el formulario mostrado es el esperado
    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, PasswordChangeForm)

    # Compruebo que el formulario tiene los campos que tiene que tener
    def test_form_inputs(self):
        self.assertContains(self.response, '<input', 4)
        self.assertContains(self.response, 'type="password"', 3)

# Compruebo que si no estas logueado el formulario te devuelva a la página de login
class LoginRequiredPasswordChangeTests(TestCase):
    def test_redirection(self):
        url = reverse('password_change')
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, f'{login_url}?next={url}')

# Clase base para comprobar los cambios de password, recibe un diccionario que será el enviado por POST al formulario
# de cambio de password
class PasswordChangeTestCase(TestCase):
    # Configuro el testcase "Base"
    def setUp(self, data={}):
        self.username = "john"
        self.old_password = "old_password"
        self.user = User.objects.create_user(username=self.username, email='john@doe.com', password=self.old_password)
        self.url = reverse('password_change')
        self.client.login(username=self.username, password=self.old_password)
        self.response = self.client.post(self.url, data)

# Compruebo un cambio de contraseña satisfactorio
class SuccessfulPasswordChangeTests(PasswordChangeTestCase):
    # Configuro el testcase con los datos que hay que enviar por post
    # con la password antigua y l que queremos que sea la nueva
    def setUp(self):
        self.nueva_password = 'new_password'
        self.old_password = "old_password"
        super().setUp({
            'old_password': self.old_password,
            'new_password1': self.nueva_password,
            'new_password2': self.nueva_password,
        })

    # Un formulario bien formado debería redirigir la usuario
    def test_redirection(self):
        self.assertRedirects(self.response, reverse('password_change_done'))

    # Compruebo que se ha cambiado efectivamente la password en la base de datos
    def test_password_changed(self):
        self.user.refresh_from_db()
        self.assertTrue( self.user.check_password( self.nueva_password ) )

    # Compruebo que el usuario puede autenticarse con la nueva password
    def test_user_authentication(self):
        response = self.client.get(reverse('home'))
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)

# Compruebo un cambio de contraseña erroneo
class InvalidPasswordChangeTests(PasswordChangeTestCase):

    # Un intento de cambio de contraseña fallido debería devolverte a la misma página
    # con un status_code de 200
    # OJO el post se ha realizado en el setUP de la clase padre y se ha hecho con el data de POST vacío
    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    # Compruebo que el formulario contiene errores
    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    # Compruebo que la password no ha sido cambiada en la base de datos
    def test_didnt_change_password(self):
        self.user.refresh_from_db()
        self.assertTrue( self.user.check_password(self.old_password) )
