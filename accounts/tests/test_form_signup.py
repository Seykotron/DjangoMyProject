from django.test import TestCase
from ..forms import SignUpForm

class SignUpFormTest(TestCase):

    # Compruebo que el formulario tiene los campos que debería
    def test_form_has_fields(self):
        form = SignUpForm()
        esperados = [ "username", "email", "password1", "password2" ]
        actuales = list(form.fields)
        self.assertSequenceEqual( esperados, actuales )
